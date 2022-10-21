from django.db import transaction
from rest_framework import serializers

from garpix_company.models.company import get_company_model
from garpix_company.models.invite import InviteToCompany
from garpix_company.models.user_company import UserCompany


Company = get_company_model()


class InviteToCompanySerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=True, help_text="ID компании")

    class Meta:
        model = InviteToCompany
        fields = ('company_id', 'email', 'is_admin')

    def create(self, validated_data):
        # getting user
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            with transaction.atomic():
                user = request.user
                company = Company.objects.get(id=validated_data['company_id'])
                try:
                    UserCompany.objects.get(company=company, user=user, is_admin=True)
                    # creating
                    obj = InviteToCompany(
                        email=validated_data['email'],
                        company_id=validated_data['company_id'],
                        is_admin=validated_data['is_admin']
                    )
                    obj.save()
                    return obj
                except UserCompany.DoesNotExist:
                    pass
        return None
