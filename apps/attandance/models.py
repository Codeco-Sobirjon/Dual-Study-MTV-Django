from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.attandance.managers import OranizationManager, OranizationDocumantManager
from django.core.exceptions import ValidationError
import os

from apps.attandance.user_manager import CustomUserManager
from config import settings


class Organization(models.Model):
    name = models.CharField(_('Tashkilot nomi'), max_length=250, null=False, blank=False)
    address = models.TextField(verbose_name="Tashkilot manzili", null=True, blank=True)
    phone = models.CharField(_('Tashkilot telefon raqami'), max_length=250, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Tashkilot ma'suli")
    objects = models.Manager()
    manager = OranizationManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("1. Tashkilot")
        verbose_name_plural = _("1. Tashkilotlar")
        ordering = ['-id']


class OrganizationDocument(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True,
                                     verbose_name="Biriktish kerak bo'lgan Tashkilot", related_name='organ_doc')
    organization_commands_file = models.FileField(verbose_name="Tashkilot buyrug'i", upload_to='org_file/', null=True,
                                                  blank=True)
    irrigation_commands_file = models.FileField(verbose_name="Tiiamebb buyrug'i", upload_to='irrigation_file/',
                                                null=True, blank=True)
    objects = models.Manager()
    manager = OranizationDocumantManager()

    def get_pdf_files(self):

        pdf_files = []

        if self.organization_commands_file and self.organization_commands_file.name.endswith('.pdf'):
            pdf_files.append(self.organization_commands_file)

        if self.irrigation_commands_file and self.irrigation_commands_file.name.endswith('.pdf'):
            pdf_files.append(self.irrigation_commands_file)

        return pdf_files

    def clean(self):

        if self.organization_commands_file and not self.organization_commands_file.name.endswith('.pdf'):
            raise ValidationError("Toshkilot buyrug'i uchun faqat PDF-fayllarga ruxsat beriladi.")

        if self.irrigation_commands_file and not self.irrigation_commands_file.name.endswith('.pdf'):
            raise ValidationError("Tiiamebb buyrug'i uchun faqat PDF fayllarga ruxsat beriladi.")


class InsGroups(models.Model):
    name = models.CharField(_('Guruh nomi'), max_length=250, null=False, blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True,
                                     verbose_name="Biriktish kerak bo'lgan Tashkilot", related_name='organ_group')
    created_at = models.DateField(verbose_name='Yaratilgan sana', null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("2. Guruh")
        verbose_name_plural = _("2. Guruhlar")
        ordering = ['-id']


class CustomUser(AbstractUser):
    username = models.CharField(unique=True, max_length=150, verbose_name='Foydalanuvchi nomi')
    email = models.EmailField(unique=True, verbose_name='Email manzili')  # Ensure email is required and unique
    ins_groups = models.ForeignKey(
        'InsGroups', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Biriktish kerak bo'lgan Guruh", related_name='group_ins'
    )
    groups = models.ManyToManyField(
        'auth.Group', related_name='customuser_set', blank=True, verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customuser_user_permissions_set', blank=True, verbose_name='user permissions'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # Use username as the primary identifier
    REQUIRED_FIELDS = ['email']  # Email is required

    def __str__(self):
        return f"{self.username}"  # Use username instead of first_name and last_name

    class Meta:
        verbose_name = _("3 Foydalanuvchilar")
        verbose_name_plural = _("3 Foydalanuvchilar")
        ordering = ['-id']


class Attandance(models.Model):
    msg_str = "Bo'sh kelsa bugun u qatnashmagan, Agar qanashgan bo'lsa ichi to'la bo'ladi"
    is_coming = models.BooleanField(default=False, null=True, blank=True, verbose_name="Davamoat")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name=f"{msg_str}", related_name='group_ins')

    created_at = models.DateField(auto_now_add=True, verbose_name='Yaratilgan sana', null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name}"

    class Meta:
        verbose_name = _("5 Davomat")
        verbose_name_plural = _("5 Davomat")
        ordering = ['-id']


class AttandanceFile(models.Model):
    file = models.ImageField(upload_to='attandance/', null=True, blank=True, verbose_name="Yuklangan fayl")
    groups = models.ForeignKey(InsGroups, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Biriktish kerak bo'lgan Guruh", related_name='attandance_group')
    created_at = models.DateField(auto_now_add=True, verbose_name='Yaratilgan sana', null=True, blank=True)

    def __str__(self):
        return self.groups.name

    class Meta:
        verbose_name = _("5 Davomat uchun yuklangan ma'lumotlar")
        verbose_name_plural = _("5 Davomat uchun yuklangan ma'lumotlar")
        ordering = ['-id']


class News(models.Model):
    title = models.CharField(_("Sarlavha"), max_length=500, null=True, blank=True)
    description = models.TextField(_("Yangilik haqidi"), null=True, blank=True)
    img = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name="Rasm qo'shish")
    created_at = models.DateField(auto_now_add=True, verbose_name='Yaratilgan sana', null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("4 Yangilik")
        verbose_name_plural = _("4 Yangiliklar")
        ordering = ['-id']


class DemandandSupply(models.Model):
    user_uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                      verbose_name="Yuboruvchi", related_name="user_uploader")
    comment = models.TextField(null=True, blank=True, verbose_name="Taklif va talablar")
    file = models.FileField(null=True, blank=True, verbose_name='Yuboliyotgan Fiyllar')
    created_at = models.DateField(auto_now_add=True, verbose_name='Yaratilgan sana', null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name = _("6 Talab va Takliflar")
        verbose_name_plural = _("6 Talab va Takliflar")
        ordering = ['-id']