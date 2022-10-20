from django.contrib import admin

from app.models import Company
from garpix_company.admin import AbstractCompanyAdmin


@admin.register(Company)
class CompanyAdmin(AbstractCompanyAdmin):
    pass
