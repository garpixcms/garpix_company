from rest_framework import permissions

from garpix_company.models import get_company_model, UserCompany, InviteToCompany

Company = get_company_model()


class CompanyOwnerOnly(permissions.BasePermission):
    """
    Доступ только для владельца компании
    """

    def has_object_permission(self, request, view, obj):

        if isinstance(obj, Company):
            return request.user.is_authenticated and request.user == obj.owner
        if isinstance(obj, UserCompany) or isinstance(obj, InviteToCompany):
            return request.user.is_authenticated and request.user == obj.company.owner
        return False
