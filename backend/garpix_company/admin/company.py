from django.contrib import admin

from garpix_company.models import UserCompany


class UserCompanyInline(admin.TabularInline):
    model = UserCompany
    extra = 0


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    readonly_fields = ('created_at', )
    inlines = (UserCompanyInline,)
