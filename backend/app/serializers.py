from django.contrib.auth import get_user_model
from rest_framework import serializers

from garpix_company.models.user_role import get_company_role_model
from garpix_company.serializers import CreateAndInviteToCompanySerializer


class CustomInviteCompanySerializer(CreateAndInviteToCompanySerializer):
    username = serializers.CharField(write_only=True)

    class Meta(CreateAndInviteToCompanySerializer.Meta):
        fields = CreateAndInviteToCompanySerializer.Meta.fields + ('username',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email')


class CompanyRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_company_role_model()
        fields = ('id', 'title')
