from rest_framework import permissions


class CompanyInviteReceiverOnly(permissions.BasePermission):
    """
    Доступ только для администратора компании
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.email == obj.email
