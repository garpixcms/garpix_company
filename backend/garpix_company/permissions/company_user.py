from rest_framework import permissions

from garpix_company.models import get_company_model, get_user_company_model

Company = get_company_model()
UserCompany = get_user_company_model()


class CompanyUserOnly(permissions.BasePermission):
    """
    Доступ только для владельца компании
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.id in UserCompany.active_objects.filter(
            company=obj).values_list('user', flat=True)
