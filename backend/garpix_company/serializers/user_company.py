from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers

from garpix_company.models.user_company import UserCompany


UserSerializer = import_string(getattr(settings, 'GARPIX_COMPANY_USER_SERIALIZER', 'garpix_company.serializers.GarpixCompanyUserSerializer'))


class UserCompanySerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserCompany
        fields = '__all__'
