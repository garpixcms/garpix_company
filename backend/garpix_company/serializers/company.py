from django.db import transaction
from rest_framework import serializers

from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import UserCompany

Company = get_company_model()


class AdminCompanySerializerMixin(serializers.Serializer):
    is_admin = serializers.SerializerMethodField(read_only=True)

    def get_is_admin(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                user_company = UserCompany.objects.filter(user=user, company=obj).first()
                if user_company is not None:
                    return user_company.is_admin
        return False


class CompanySerializer(AdminCompanySerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'id', 'title', 'full_title', 'inn', 'ogrn',
            'kpp', 'bank_title', 'bic', 'schet', 'korschet',
            'ur_address', 'fact_address', 'is_admin'
        )


class CreateCompanySerializer(AdminCompanySerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'title', 'full_title', 'inn', 'ogrn', 'kpp', 'bank_title', 'bic', 'schet', 'korschet',
                  'ur_address', 'fact_address', 'is_admin')

    def create(self, validated_data):
        with transaction.atomic():
            # getting user
            user = None
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            # creating
            obj = Company(
                title=validated_data['title'],
                full_title=validated_data['full_title'],
                inn=validated_data['inn'],
                ogrn=validated_data['ogrn'],
                kpp=validated_data['kpp'],
                bank_title=validated_data['bank_title'],
                bic=validated_data['bic'],
                schet=validated_data['schet'],
                korschet=validated_data['korschet'],
                ur_address=validated_data['ur_address'],
                fact_address=validated_data['fact_address'],
            )
            obj.save()
            user_company = UserCompany(user=user, company=obj, is_admin=True)
            user_company.save()
        return obj


class UpdateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title', 'full_title', 'inn', 'ogrn', 'kpp', 'bank_title',
            'bic', 'schet', 'korschet', 'ur_address', 'fact_address'
        )
