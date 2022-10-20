from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.invite import InviteToCompany
from garpix_company.permissions import CompanyAdminOnly
from garpix_company.permissions.invite_receiver import CompanyInviteReceiverOnly
from garpix_company.serializers import InviteToCompanySerializer


class InviteToCompanyViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet, GarpixCompanyViewSetMixin):
    """
    Список участников компании
    """
    queryset = InviteToCompany.created_objects.all()
    serializer_class = InviteToCompanySerializer
    permission_classes = [permissions.IsAdminUser | CompanyInviteReceiverOnly]
    permission_classes_by_action = {
        'create': [permissions.IsAdminUser | CompanyAdminOnly]
    }
    lookup_field = 'token'

    def get_serializer_class(self):
        return InviteToCompanySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def accept(self, request, token=None):
        invite = self.get_object()
        result, message = invite.accept()
        if result:
            serializer = InviteToCompanySerializer(invite)
            return Response(serializer.data)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def decline(self, request, token=None):
        invite = self.get_object()
        invite.decline()
        serializer = InviteToCompanySerializer(invite)
        return Response(serializer.data)
