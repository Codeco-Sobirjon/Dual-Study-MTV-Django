from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from urllib.parse import urlparse, parse_qs
from django.utils import timezone
from datetime import date, timedelta
from apps.attandance.models import (
    News, Organization,
    OrganizationDocument, InsGroups, Attandance, AttandanceFile, CustomUser, DemandandSupply
)
from django.urls import reverse
from django.contrib.auth.models import Group


def login_attendance(request, format=None, *args, **kwargs):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)
        if not username or not password:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            auth_login(request, user)

            if user.groups.filter(name='Student').exists():
                return redirect('student_dashboard')
            elif user.groups.filter(name='Nazoratchi').exists():
                return redirect('checker_dashboard')
            elif user.groups.filter(name='Tashkilot').exists():
                return redirect('organization_dashboard')
            else:
                messages.error(request, "Noto'g'ri foydalanuvchi roli.")
                return render(request, 'login.html')
        else:
            messages.error(request, "Noto'g'ri login yoki parol. Iltimos, qaytadan urinib ko'ring.")
            return render(request, 'login.html')

    return render(request, 'login.html')


@login_required
def logout_attandance(request):
    logout(request)
    return redirect('login')


@login_required
def index(request, format=None, *args, **kwargs):
    news_list = News.objects.all().order_by('-id')
    paginator = Paginator(news_list, 4)  # Show 3 news items per page

    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)

    context = {
        'last_news': News.objects.order_by('-id')[:5],
        'news': news,
    }
    return render(request, 'index.html', context)


def commands(request, format=None, *args, **kwargs):
    user = request.user
    get_organization = Organization.manager.filter_by_user(user)
    get_organization_doc = OrganizationDocument.manager.filter_by_organization(get_organization)

    if get_organization_doc:

        context = {
            'documant1_url': get_organization_doc.organization_commands_file.url if get_organization_doc.organization_commands_file else None,
            'documant2_url': get_organization_doc.irrigation_commands_file.url if get_organization_doc.irrigation_commands_file else None
        }

        return render(request, 'command.html', context)

    context = {
        'documant1_url': None,
        'documant2_url': None
    }

    return render(request, 'command.html', context)


@login_required
def groups_student(request, format=None, *args, **kwargs):
    user = request.user
    get_organization = Organization.manager.filter_by_user(user)
    group_id = request.GET.get('group', 0)

    if group_id:
        group = InsGroups.objects.filter(id=group_id).first()
        if group:
            group_data = CustomUser.objects.filter(ins_groups=group)
            attendance_data = [
                {
                    "student": f"{student.first_name} {student.last_name}",
                    "date": record.created_at,
                    "coming": record.is_coming
                }
                for student in group_data
                for record in Attandance.objects.filter(student=student)
            ]
        else:
            group_data = []
            attendance_data = []
    else:
        group_data = []
        attendance_data = []

    groups = InsGroups.objects.select_related('organization').filter(organization=get_organization)

    context = {
        'group_list': groups,
        'group_data': group_data,
        'attendance_data': attendance_data
    }
    return render(request, 'group.html', context)


@login_required
def add_attendance(request):
    if request.method == 'POST':
        students = request.POST.getlist('students')
        file = request.FILES.get('file')
        attendance_date = request.POST.get('date') or date.today()

        if not isinstance(attendance_date, date):
            try:
                attendance_date = timezone.datetime.strptime(attendance_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

        for student_id in students:
            Attandance.objects.get_or_create(
                student_id=student_id,
                created_at=attendance_date,
                defaults={'is_coming': True}
            )

        referer_url = request.META.get('HTTP_REFERER', 'groups_student')
        group_id = parse_qs(urlparse(referer_url).query).get('group', [None])[0]

        if group_id and file:
            group_instance = get_object_or_404(InsGroups, id=group_id)
            AttandanceFile.objects.create(file=file, groups=group_instance)

        return redirect(referer_url)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def student_dashboard(request):
    user = request.user
    attendance_list = Attandance.objects.filter(student=user)

    if attendance_list.exists():

        first_attendance = attendance_list.order_by('created_at').first().created_at
        last_attendance = attendance_list.order_by('-created_at').first().created_at
        total_days = (last_attendance - first_attendance).days
        all_dates = [first_attendance + timedelta(days=i) for i in range(total_days)]

        attended_dates = set(attendance.created_at for attendance in attendance_list)
        missing_dates = [date for date in all_dates if date not in attended_dates]

        context = {
            'attendance_list': attendance_list,
            'first_attendance_date': first_attendance,
            'last_attendance_date': last_attendance,
            'attended_dates': list(attended_dates),
            'missing_dates': missing_dates,
        }
    else:
        context = {
            'attendance_list': attendance_list,
            'message': "No attendance records found."
        }

    return render(request, 'stu_dash.html', context)


@login_required
def checker_dashboard(request):
    user = request.user
    # Get all organizations the user is associated with
    get_organization = list(Organization.objects.values_list('id', flat=True))

    group_id = request.GET.get('group', None)  # Default to None if not provided

    group_data = []
    attendance_data = []
    list_not_coming = []

    if group_id:
        group = InsGroups.objects.filter(id=group_id).first()  # Get the first match or None
        if group:
            group_data = CustomUser.objects.filter(ins_groups=group)
            for student in group_data:
                records = Attandance.objects.filter(student=student).order_by('created_at')
                if records.exists():
                    # Prepare attendance records
                    attendance_records = [
                        {"date": record.created_at, "coming": record.is_coming} for record in records
                    ]
                    attendance_data.append({
                        "student": f"{student.first_name} {student.last_name}",
                        "attendance_records": attendance_records
                    })

                    # Check for dates with no attendance
                    first_record = records.first()
                    last_record = records.last()
                    attendance_dates = [record.created_at for record in records]
                    all_dates = [first_record.created_at + timezone.timedelta(days=i) for i in range((last_record.created_at - first_record.created_at).days + 1)]
                    non_attendance_dates = set(all_dates) - set(attendance_dates)
                    list_not_coming.append({
                        "student": f"{student.first_name} {student.last_name}",
                        "missing_dates": non_attendance_dates
                    })

    # Fetch all groups associated with the user's organizations
    groups = InsGroups.objects.select_related('organization').filter(organization__in=get_organization)

    context = {
        'group_list': groups,
        'group_data': group_data,
        'attendance_data': attendance_data,
        'list_not_coming': list_not_coming
    }
    return render(request, 'checker_dash.html', context)


@login_required
def demand_supply_create(request):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        file = request.FILES.get('file')
        demand = DemandandSupply(
            user_uploader=request.user,
            comment=comment,
            file=file
        )
        demand.save()
        return redirect('demand_supply_create')

    return render(request, 'demand_supply_form.html')


@login_required
def demand_supply_create_for_student(request):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        file = request.FILES.get('file')
        demand = DemandandSupply(
            user_uploader=request.user,
            comment=comment,
            file=file
        )
        demand.save()
        return redirect('demand_supply_create_for_student')

    return render(request, 'demand_supply_form_student.html')