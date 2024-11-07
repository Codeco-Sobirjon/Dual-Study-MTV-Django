from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import (
    Organization, InsGroups, Attandance, OrganizationDocument, News, AttandanceFile, CustomUser, DemandandSupply
)
from import_export.admin import ImportExportModelAdmin

from .resources import CustomUserResource


admin.site.site_header = "Davomat Platformasi"
admin.site.site_title = "Davomat Platformasi"
admin.site.index_title = "Xush kelibsiz Dual ta'lim va davmoat platformasi"

admin.site.unregister(Group)

Group._meta.verbose_name = _("Rollar")
Group._meta.verbose_name_plural = _("Rollar")

@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    pass


class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = CustomUserResource
    list_display = ('username', 'first_name', 'last_name', 'email', 'ins_groups')
    list_filter = ('ins_groups', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-id',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'ins_groups')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'ins_groups', 'is_active', 'is_staff')
        }),
    )


class CustomUserInline(admin.TabularInline):
    model = CustomUser
    extra = 1
    verbose_name = "Students"
    verbose_name_plural = "Students"


class OrganizationDocumentInline(admin.TabularInline):
    model = OrganizationDocument
    extra = 1
    verbose_name = "Organization Orders"
    verbose_name_plural = "Organization Orders"


class AttandanceStudentInline(admin.TabularInline):
    model = Attandance
    extra = 1
    verbose_name = "Attendance"
    verbose_name_plural = "Attendance"
    fields = ('student', 'is_coming', 'formatted_created_at')
    readonly_fields = ('formatted_created_at',)

    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else '-'
    formatted_created_at.short_description = 'Created Date'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'author')
    search_fields = ('name', 'address')
    list_filter = ('author',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            group_name = "Tashkilot"
            kwargs["queryset"] = CustomUser.objects.filter(groups__name=group_name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    inlines = [OrganizationDocumentInline]


@admin.register(InsGroups)
class InsGroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at')
    search_fields = ('name', 'organization__name')
    list_filter = ('created_at', 'organization')
    inlines = [CustomUserInline]


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(AttandanceFile)
class AttandanceFileAdmin(admin.ModelAdmin):
    list_display = ['groups', 'created_at']


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(DemandandSupply)
class DemandandSupplyAdmin(admin.ModelAdmin):
    list_display = ['user_uploader', 'get_user_groups', 'created_at']
    list_filter = ['user_uploader__groups']

    def get_user_groups(self, obj):
        return ", ".join([group.name for group in obj.user_uploader.groups.all()])
    get_user_groups.short_description = 'User Groups'