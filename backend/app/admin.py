from django.contrib import admin

from app.models import Company
from garpix_company.admin import CompanyAdmin


@admin.register(Company)
class CompanyAdmin(CompanyAdmin):
    pass
