from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.user_company import UserCompany
from garpix_company.permissions import CompanyAdminOnly
from garpix_company.serializers.user_company import UserCompanySerializer
from django.utils.translation import ugettext_lazy as _


class UserCompanyViewSet(GarpixCompanyViewSetMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = [IsAdminUser | CompanyAdminOnly]
    queryset = UserCompany.objects.all()
    serializer_class = UserCompanySerializer
    lookup_field = 'user'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        result, message = instance.kick(request.user.id)
        if result:
            return Response({'status': _('Пользователь успешно удален')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def block(self, request, *args, **kwargs):
        instance = self.get_object()
        result, message = instance.block(request.user.id)
        if result:
            return Response({'status': _('Пользователь успешно заблокирован')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def unblock(self, request, *args, **kwargs):
        instance = self.get_object()
        result, message = instance.unblock(request.user.id)
        if result:
            return Response({'status': _('Пользователь успешно разблокирован')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def set_admin(self, request, *args, **kwargs):
        instance = self.get_object()
        result, message = instance.set_admin(request.user.id)
        if result:
            return Response({'status': _('Пользователь успешно назначен админом')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def unset_admin(self, request, *args, **kwargs):
        instance = self.get_object()
        result, message = instance.unset_admin(request.user.id)
        if result:
            return Response({'status': _('Пользователь больше не админ')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)
