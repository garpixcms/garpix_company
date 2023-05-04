from rest_framework import permissions

from garpix_company.models import get_company_model, get_user_company_model, InviteToCompany
from garpix_company.services.role_service import UserCompanyRoleService

Company = get_company_model()
UserCompany = get_user_company_model()


class CompanyAdminOnly(permissions.BasePermission):
    """
    Доступ только для администратора компании
    """

    def has_object_permission(self, request, view, obj):
        company_role_service = UserCompanyRoleService()

        if isinstance(obj, Company):
            return request.user.is_authenticated and request.user.id in obj.user_companies.filter(
                role=company_role_service.get_admin_role()).values_list('user', flat=True)
        if isinstance(obj, InviteToCompany) or isinstance(obj, UserCompany):
            return request.user.is_authenticated and obj.company.user_companies.filter(
                role=company_role_service.get_admin_role(), user=request.user)
        return False
