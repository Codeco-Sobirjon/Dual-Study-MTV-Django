from django.urls import path
from apps.attandance.views import *


urlpatterns = [
    path('', login_attendance, name='login'),
    path('logout/', logout_attandance, name='logout'),
    path('organization/dashboard/', index, name='organization_dashboard'),
    path('student/dashboard', student_dashboard, name='student_dashboard'),
    path('checker/dashboard', checker_dashboard, name='checker_dashboard'),
    path('commands/', commands, name='commands'),
    path('group/student/', groups_student, name='groups_student'),
    path('add-attendance/', add_attendance, name='add_attendance'),
    path('demand/supply/create', demand_supply_create, name='demand_supply_create'),
    path('demand/suplly/create/student', demand_supply_create_for_student, name='demand_supply_create_for_student'),
]