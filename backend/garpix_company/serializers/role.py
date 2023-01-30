from rest_framework import serializers

from garpix_company.models.user_role import get_company_role_model


class GarpixCompanyRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_company_role_model()
        fields = ('id', 'title', 'role_type')
