# custom_auth_config.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomAuthConfig(AppConfig):
    name = 'django.contrib.auth'
    verbose_name = _("Rollashtirish")  # Your desired name
