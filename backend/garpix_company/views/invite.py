from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.invite import InviteToCompany
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly
from garpix_company.permissions.invite_receiver import CompanyInviteReceiverOnly
from garpix_company.serializers import InviteToCompanySerializer


class InviteToCompanyViewSet(GarpixCompanyViewSetMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    Список участников компании
    """
    queryset = InviteToCompany.created_objects.all()
    serializer_class = InviteToCompanySerializer
    permission_classes = [permissions.IsAdminUser | CompanyAdminOnly | CompanyOwnerOnly | CompanyInviteReceiverOnly]

    # lookup_field = 'token'  # TODO сделать вариант инвайта по токену

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InviteToCompanySerializer
        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def accept(self, request, pk):
        invite = self.get_object()
        self.check_object_permissions(request, invite)
        result, message = invite.accept()
        if result:
            serializer = InviteToCompanySerializer(invite)
            return Response(serializer.data)
        return Response({'non_field_error': [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def decline(self, request, pk):
        invite = self.get_object()
        self.check_object_permissions(request, invite)
        invite.decline()
        serializer = InviteToCompanySerializer(invite)
        return Response(serializer.data)
