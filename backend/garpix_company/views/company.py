from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models import InviteToCompany
from garpix_company.models.company import get_company_model
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly
from garpix_company.serializers import CompanySerializer, CreateCompanySerializer, UpdateCompanySerializer, \
    ChangeOwnerCompanySerializer, CreateAndInviteToCompanySerializer, InviteToCompanySerializer
from django.utils.translation import ugettext_lazy as _

Company = get_company_model()


class CompanyViewSet(GarpixCompanyViewSetMixin, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']
    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'retrieve': [AllowAny],
                                    'list': [AllowAny],
                                    'update': [IsAdminUser | CompanyAdminOnly],
                                    'partial_update': [IsAdminUser | CompanyAdminOnly],
                                    'destroy': [IsAdminUser | CompanyAdminOnly],
                                    'change_owner': [IsAdminUser | CompanyOwnerOnly],
                                    'invite': [CompanyAdminOnly | CompanyOwnerOnly],
                                    'create_and_invite': [CompanyAdminOnly | CompanyOwnerOnly],
                                    'invites': [AllowAny]
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
        if self.action in ['invite', 'invites']:
            return InviteToCompanySerializer
        return CompanySerializer

    @action(detail=True, methods=['POST'])
    def change_owner(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serializer = ChangeOwnerCompanySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result, message = company.change_owner(serializer.data['new_owner'], request.user)
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

    @action(methods=['get'], detail=True, serializer_class=InviteToCompanySerializer(many=True))
    def invites(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        queryset = InviteToCompany.objects.filter(company=company)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
