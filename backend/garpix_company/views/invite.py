from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.invite import InviteToCompany
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly
from garpix_company.permissions.invite_receiver import CompanyInviteReceiverOnly
from garpix_company.serializers import InviteToCompanySerializer


CreateAndInviteToCompanySerializer = import_string(getattr(settings, 'GARPIX_COMPANY_CREATE_AND_INVITE_SERIALIZER', 'garpix_company.serializers.CreateAndInviteToCompanySerializer'))


class InviteToCompanyViewSet(GarpixCompanyViewSetMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    Список участников компании
    """
    queryset = InviteToCompany.created_objects.all()
    serializer_class = InviteToCompanySerializer
    permission_classes = [CompanyInviteReceiverOnly]
    permission_classes_by_action = {
        'create': [permissions.IsAdminUser, CompanyAdminOnly, CompanyOwnerOnly],
        'create_and_invite': [permissions.IsAdminUser, CompanyAdminOnly, CompanyOwnerOnly],
    }
    lookup_field = 'token'

    def get_serializer_class(self):
        if self.action == 'create_and_invite':
            return CreateAndInviteToCompanySerializer
        return InviteToCompanySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def create_and_invite(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
