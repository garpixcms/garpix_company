from rest_framework import serializers

from garpix_company.serializers import CreateAndInviteToCompanySerializer


class CustomInviteCompanySerializer(CreateAndInviteToCompanySerializer):
    username = serializers.CharField(write_only=True)

    class Meta(CreateAndInviteToCompanySerializer.Meta):
        fields = CreateAndInviteToCompanySerializer.Meta.fields + ('username',)
