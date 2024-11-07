from django.db import models
from apps.attandance.models import *


class OranizationQuerySet(models.QuerySet):

    def filter_by_user(self, user):
        return self.select_related('author').filter(author=user).first()


class OranizationDocumantQuerySet(models.QuerySet):

    def filter_by_organization(self, organization):
        return self.select_related('organization').filter(organization=organization).first()


class OranizationManager(models.Manager):
    def get_queryset(self):
        return OranizationQuerySet(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)


class OranizationDocumantManager(models.Manager):
    def get_queryset(self):
        return OranizationDocumantQuerySet(self.model, using=self._db)

    def filter_by_organization(self, organization):
        return self.get_queryset().filter_by_organization(organization)
