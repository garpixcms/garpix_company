from django.db import models

from garpix_company.helpers import COMPANY_STATUS_ENUM


class CompanyActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=COMPANY_STATUS_ENUM.ACTIVE)
