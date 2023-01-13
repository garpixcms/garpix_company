from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import UserCompany
from django.utils.translation import ugettext_lazy as _

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

    def get_field_names(self, declared_fields, info):
        expanded_fields = super().get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class CompanySerializer(AdminCompanySerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Company
        exclude = ('participants',)
        extra_fields = ['is_admin']


class CreateCompanySerializer(AdminCompanySerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Company
        exclude = ('participants', 'owner')
        extra_fields = ['is_admin']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def create(self, validated_data):
        with transaction.atomic():
            # getting user
            user = None
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            else:
                raise ValidationError(_("Необходима авторизация"))
            # creating
            obj = Company(
                owner=user,
                **validated_data
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


class ChangeOwnerCompanySerializer(serializers.Serializer):
    new_owner = serializers.IntegerField()
