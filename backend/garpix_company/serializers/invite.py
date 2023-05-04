from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.module_loading import import_string
from garpix_utils.string import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from garpix_company.models import get_user_company_model
from garpix_company.models.company import get_company_model
from garpix_company.models.invite import InviteToCompany
from django.utils.translation import ugettext_lazy as _
from garpix_company.models.user_role import get_company_role_model


RoleSerializer = import_string(getattr(settings, 'GARPIX_COMPANY_ROLE_SERIALIZER', 'garpix_company.serializers.role.GarpixCompanyRoleSerializer'))
UserCompany = get_user_company_model()


class InviteToCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = InviteToCompany
        fields = ('email', 'user', 'role')
        extra_kwargs = {
            'role': {'required': True},
        }

    def validate_email(self, value):
        User = get_user_model()
        Company = get_company_model()
        company_id = self.context.get("company_id")
        try:
            user = User.objects.get(email=value)
            if not Company.check_user_companies_limit(user):
                raise ValidationError(_('У пользователя с указанным email превышен лимит количества компаний'))
            if UserCompany.active_objects.filter(user=user, company_id=company_id).exists():
                raise ValidationError(_('Указанный пользователь уже является сотрудником компании'))
        except User.DoesNotExist:
            raise ValidationError(_('Пользователь с указанным email не зарегистрирован'))
        return value

    def validate_user(self, value):
        Company = get_company_model()
        company_id = self.context.get("company_id")
        if not Company.check_user_companies_limit(value):
            raise ValidationError(_('У пользователя с указанным id превышен лимит количества компаний'))
        if UserCompany.active_objects.filter(user=value, company_id=company_id).exists():
            raise ValidationError(_('Указанный пользователь уже является сотрудником компании'))
        return value

    def validate(self, data):
        validated_data = super().validate(data)
        user = validated_data.get('user', None)
        email = validated_data.get('email', None)
        if not user and not email:
            raise ValidationError(_('Укажите email или id пользователя'))
        if user:
            data['email'] = user.email
        return data

    def create(self, validated_data):
        Role = get_company_role_model()
        request = self.context.get("request")
        company_id = self.context.get("company_id")
        if role := validated_data.get('role', None):
            if role.role_type == Role.ROLE_TYPE.OWNER:
                raise ValidationError({'role': [_('Нельзя пригласить пользователя на роль владельца')]})
        if request and hasattr(request, "user") and request.user.is_authenticated:
            with transaction.atomic():
                # creating
                obj = InviteToCompany(
                    company_id=company_id,
                    **validated_data
                )
                obj.save()
                return obj
        pass


class CreateAndInviteToCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = InviteToCompany
        fields = ('email', 'role')
        extra_kwargs = {
            'role': {'required': True},
        }

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).first():
            raise ValidationError(_('Пользователь с указанным email уже зарегистрирован'))
        return value

    def create(self, validated_data):
        User = get_user_model()
        Role = get_company_role_model()
        request = self.context.get("request")
        company_id = self.context.get("company_id")
        if role := validated_data.pop('role', None):
            if role.role_type == Role.ROLE_TYPE.OWNER:
                raise ValidationError({'role': [_('Нельзя пригласить пользователя на роль владельца')]})
        if request and hasattr(request, "user") and request.user.is_authenticated:
            with transaction.atomic():
                if 'username' not in validated_data.keys():
                    validated_data['username'] = get_random_string(25)
                if 'password' not in validated_data.keys():
                    validated_data['password'] = User.objects.make_random_password()
                user = User.objects.create_user(**validated_data)
                invite_data = {
                    'email': validated_data['email'],
                    'company_id': company_id,
                    'role': role,
                    'user': user
                }
                obj = InviteToCompany(**invite_data)
                obj.save()
                return obj
        return None


class InvitesSerializer(serializers.ModelSerializer):

    role = RoleSerializer()

    class Meta:
        model = InviteToCompany
        fields = '__all__'
