from rest_framework.generics import get_object_or_404
from rest_framework import status, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models import get_company_model
from garpix_company.models.user_company import UserCompany
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly
from garpix_company.serializers.user_company import UserCompanySerializer, ChangeUserRoleSerializer
from django.utils.translation import ugettext_lazy as _


class UserCompanyViewSet(GarpixCompanyViewSetMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = [CompanyAdminOnly | CompanyOwnerOnly]
    queryset = UserCompany.active_objects.all()
    serializer_class = UserCompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__email']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserCompanySerializer
        if self.action == 'change_role':
            return ChangeUserRoleSerializer
        return None

    def get_queryset(self, *args, **kwargs):
        Company = get_company_model()
        company_pk = self.kwargs.get("company_pk")
        company = get_object_or_404(Company.objects.all(), id=company_pk)
        if self.action not in ['unblock', 'destroy']:
            return self.queryset.filter(company=company)
        return UserCompany.objects.filter(company=company)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        result, message = instance.kick()
        if result:
            return Response({'status': _('success')}, status=status.HTTP_200_OK)
        return Response({'non_field_error': [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def block(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        result, message = instance.block()
        if result:
            return Response({'status': _('success')}, status=status.HTTP_200_OK)
        return Response({'non_field_error': [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def unblock(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        result, message = instance.unblock()
        if result:
            return Response({'status': _('success')}, status=status.HTTP_200_OK)
        return Response({'non_field_error': [message]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def change_role(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result, message = instance.change_role(role=serializer.data['role'])
        if result:
            return Response({'status': _('success')}, status=status.HTTP_200_OK)
        return Response({'non_field_error': [message]}, status=status.HTTP_400_BAD_REQUEST)
