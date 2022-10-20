from rest_framework import serializers

from garpix_company.models.user_company import UserCompany


class UserCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCompany
        fields = '__all__'
