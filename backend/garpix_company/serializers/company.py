from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import UserCompany
from django.utils.translation import ugettext_lazy as _

from garpix_company.models.user_role import get_company_role_model
from garpix_company.services.role_service import UserCompanyRoleService

Company = get_company_model()
CompanyRole = get_company_role_model()


class AdminCompanySerializerMixin(serializers.Serializer):
    is_admin = serializers.SerializerMethodField(read_only=True)

    def get_is_admin(self, obj):
        company_role_service = UserCompanyRoleService()

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                user_company = UserCompany.objects.filter(user=user, company=obj).first()
                if user_company is not None:
                    return user_company.role == company_role_service.get_admin_role()
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

    user_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Company
        exclude = ('participants',)
        extra_fields = ['is_admin', 'user_by']
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

            CompanyRole = get_company_role_model()
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


class UpdateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title', 'full_title', 'inn', 'ogrn', 'kpp', 'bank_title',
            'bic', 'schet', 'korschet', 'ur_address', 'fact_address'
        )


class ChangeOwnerCompanySerializer(serializers.Serializer):
    new_owner = serializers.IntegerField()
