from rest_framework import permissions

from garpix_company.models import get_company_model, UserCompany, InviteToCompany
from garpix_company.models.user_role import get_company_role_model

Company = get_company_model()
CompanyRole = get_company_role_model()


class CompanyAdminOnly(permissions.BasePermission):
    """
    Доступ только для администратора компании
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Company):
            return request.user.is_authenticated and request.user.id in obj.user_companies.filter(
                role=CompanyRole.get_admin_role()).values_list('user', flat=True)
        if isinstance(obj, InviteToCompany) or isinstance(obj, UserCompany):
            return request.user.is_authenticated and obj.company.user_companies.filter(
                role=CompanyRole.get_admin_role(), user=request.user)
        return False
