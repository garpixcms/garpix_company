from django.conf import settings
from django.utils.module_loading import import_string
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from garpix_company.helpers import CHOICES_INVITE_STATUS_ENUM
from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models import InviteToCompany
from garpix_company.models.company import get_company_model
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly, CompanyUserOnly
from garpix_company.serializers import CompanySerializer, CreateCompanySerializer, UpdateCompanySerializer, \
    ChangeOwnerCompanySerializer, InviteToCompanySerializer, InvitesSerializer
from django.utils.translation import ugettext_lazy as _

Company = get_company_model()

CreateAndInviteToCompanySerializer = import_string(getattr(settings, 'GARPIX_COMPANY_CREATE_AND_INVITE_SERIALIZER',
                                                           'garpix_company.serializers.CreateAndInviteToCompanySerializer'))


class CompanyViewSet(GarpixCompanyViewSetMixin, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']
    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'retrieve': [CompanyUserOnly],
                                    'list': [IsAdminUser],
                                    'update': [CompanyOwnerOnly],
                                    'partial_update': [CompanyOwnerOnly],
                                    'destroy': [CompanyOwnerOnly],
                                    'change_owner': [CompanyOwnerOnly],
                                    'invite': [CompanyAdminOnly | CompanyOwnerOnly],
                                    'create_and_invite': [CompanyAdminOnly | CompanyOwnerOnly],
                                    'invites': [CompanyAdminOnly | CompanyOwnerOnly]
                                    }

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCompanySerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCompanySerializer
        if self.action == 'change_owner':
            return ChangeOwnerCompanySerializer
        if self.action == 'create_and_invite':
            return CreateAndInviteToCompanySerializer
        if self.action == 'invites':
            return InvitesSerializer
        if self.action == 'invite':
            return InviteToCompanySerializer
        return CompanySerializer

    @action(detail=True, methods=['POST'])
    def change_owner(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serializer = ChangeOwnerCompanySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result, message = company.change_owner(serializer.data, request.user)
        if result:
            return Response({'status': _('Владелец успешно изменен')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def invite(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serializer = self.get_serializer(data=request.data)
        serializer.context.update({'company_id': pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['post'], detail=True)
    def create_and_invite(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serializer = self.get_serializer(data=request.data)
        serializer.context.update({'company_id': pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(parameters=[
        OpenApiParameter(
            name='status',
            type=str,
            enum=[choice[0] for choice in CHOICES_INVITE_STATUS_ENUM.CHOICES]
        ),
    ])
    @action(methods=['get'], detail=True)
    def invites(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        queryset = InviteToCompany.objects.filter(company=company)
        if invite_status := request.GET.get('status', None):
            queryset = queryset.filter(status=invite_status)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
