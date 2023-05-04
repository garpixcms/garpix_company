from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import get_user_company_model
from django.utils.translation import ugettext_lazy as _

from garpix_company.models.user_role import get_company_role_model
from garpix_company.services.role_service import UserCompanyRoleService

Company = get_company_model()
CompanyRole = get_company_role_model()
UserCompany = get_user_company_model()


class ExtraFieldsCompanySerializerMixin(serializers.Serializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super().get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class CompanySerializer(ExtraFieldsCompanySerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Company
        exclude = ('participants',)


class CreateCompanySerializer(ExtraFieldsCompanySerializerMixin, serializers.ModelSerializer):

    user_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Company
        exclude = ('participants',)
        extra_fields = ['user_by']
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def validate_user_by(self, value):
        Company = get_company_model()
        if not Company.check_user_companies_limit(value):
            raise ValidationError(_('У вас превышен лимит количества компаний'))
        return value

    def create(self, validated_data):
        with transaction.atomic():

            company_role_service = UserCompanyRoleService()
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            else:
                raise ValidationError(_("Необходима авторизация"))
            # creating
            validated_data.pop('user_by')
            obj = Company(
                **validated_data
            )
            obj.save()
            user_company = UserCompany(user=user, company=obj, role=company_role_service.get_owner_role())
            user_company.save()
        return obj


class UpdateCompanySerializer(ExtraFieldsCompanySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title', 'full_title', 'inn', 'ogrn', 'kpp', 'bank_title',
            'bic', 'schet', 'korschet', 'ur_address', 'fact_address'
        )


class ChangeOwnerCompanySerializer(serializers.ModelSerializer):
    new_owner = serializers.IntegerField()
    stay_in_company = serializers.BooleanField(required=False)

    class Meta:
        model = UserCompany
        fields = ('new_owner', 'role', 'stay_in_company')
        extra_kwargs = {
            'role': {'required': False}
        }
