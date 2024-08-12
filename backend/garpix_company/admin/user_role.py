from django.contrib import admin
from ..models import get_user_company_model, get_company_role_model


UserCompany = get_user_company_model()
UserCompanyRole = get_company_role_model()


class UserCompanyRoleAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj is None or 'role_type' in readonly_fields:
            return readonly_fields

        if obj.role_type != UserCompanyRole.ROLE_TYPE.OWNER or not self._is_role_used(obj):
            return readonly_fields

        return [*readonly_fields, 'role_type']

    def has_delete_permission(self, request, obj=None) -> bool:
        if obj is None:
            return True
        return not self._is_role_used(obj)

    def _is_role_used(self, obj):
        return UserCompany.objects.filter(role=obj.pk).exists()
