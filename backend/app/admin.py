from django.contrib import admin

from app.models import Company, UserCompanyRole
from garpix_company.admin import CompanyAdmin


@admin.register(Company)
class CompanyAdmin(CompanyAdmin):
    pass


@admin.register(UserCompanyRole)
class UserCompanyRoleAdmin(admin.ModelAdmin):
    pass
