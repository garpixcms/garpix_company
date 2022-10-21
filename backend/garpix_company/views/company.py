from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from garpix_company.mixins.views import GarpixCompanyViewSetMixin
from garpix_company.models.company import get_company_model
from garpix_company.permissions import CompanyAdminOnly
from garpix_company.serializers import CompanySerializer, CreateCompanySerializer, UpdateCompanySerializer

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
                                    'destroy': [IsAdminUser | CompanyAdminOnly]}

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
        return CompanySerializer
