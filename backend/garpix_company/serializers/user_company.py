from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers

from garpix_company.models.user_company import UserCompany


UserSerializer = import_string(getattr(settings, 'GARPIX_COMPANY_USER_SERIALIZER', 'garpix_company.serializers.GarpixCompanyUserSerializer'))
RoleSerializer = import_string(getattr(settings, 'GARPIX_COMPANY_ROLE_SERIALIZER', 'garpix_company.serializers.role.GarpixCompanyRoleSerializer'))


class UserCompanySerializer(serializers.ModelSerializer):

    user = UserSerializer()
    role = RoleSerializer()

    class Meta:
        model = UserCompany
        fields = '__all__'


class ChangeUserRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCompany
        fields = ('role',)
