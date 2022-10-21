from rest_framework import permissions

from garpix_company.models import get_company_model, UserCompany, InviteToCompany

Company = get_company_model()


class CompanyAdminOnly(permissions.BasePermission):
    """
    Доступ только для администратора компании
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Company):
            return request.user.is_authenticated and request.user.id in obj.usercompany_set.filter(
                is_admin=True).values_list('user', flat=True)
        if isinstance(obj, UserCompany):
            return request.user.is_authenticated and request.user == obj.user
        if isinstance(obj, InviteToCompany):
            return request.user.is_authenticated and obj.company.usercompany_set.filter(
                is_admin=True, user=request.user)
