from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.company import get_company_model
from garpix_company.permissions import CompanyAdminOnly, CompanyOwnerOnly
from garpix_company.serializers import CompanySerializer, CreateCompanySerializer, UpdateCompanySerializer, \
    ChangeOwnerCompanySerializer
from django.utils.translation import ugettext_lazy as _

Company = get_company_model()


class CompanyViewSet(ModelViewSet, GarpixCompanyViewSetMixin):
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
                                    'change_owner': [IsAdminUser | CompanyOwnerOnly]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCompanySerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCompanySerializer
        if self.action == 'change_owner':
            return ChangeOwnerCompanySerializer
        return CompanySerializer

    @action(detail=True, methods=['POST'])
    def change_owner(self, request, pk):
        company = self.get_object()
        serializer = ChangeOwnerCompanySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result, message = company.change_owner(serializer.data['new_owner'], request.user)
        if result:
            return Response({'status': _('Владелец успешно изменен')}, status=status.HTTP_200_OK)
        return Response({"non_field_error": [message]}, status=status.HTTP_400_BAD_REQUEST)
