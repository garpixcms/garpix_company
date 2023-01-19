from django.contrib.auth import get_user_model
from django.db import transaction
from garpix_utils.string import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from garpix_company.models.company import get_company_model
from garpix_company.models.invite import InviteToCompany
from django.utils.translation import ugettext_lazy as _


class InviteToCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = InviteToCompany
        fields = ('email', 'is_admin', 'role')

    def validate_email(self, value):
        User = get_user_model()
        Company = get_company_model()
        try:
            user = User.objects.get(email=value)
            if not Company.check_user_companies_limit(user):
                raise ValidationError(_(f'У пользователя с указанным email превышен лимит количества компаний'))
        except User.DoesNotExist:
            raise ValidationError(_('Пользователь с указанным email не зарегистрирован'))
        return value

    def create(self, validated_data):
        Company = get_company_model()
        # getting user
        user = None
        request = self.context.get("request")
        company_id = self.context.get("company_id")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            with transaction.atomic():
                # creating
                obj = InviteToCompany(
                    email=validated_data['email'],
                    company_id=company_id,
                    is_admin=validated_data['is_admin'],
                    role=validated_data.get('role', None)
                )
                obj.save()
                return obj
        pass


class CreateAndInviteToCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = InviteToCompany
        fields = ('email', 'is_admin', 'role')

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).first():
            ValidationError(_('Пользователь с указанным email уже зарегистрирован'))
        return value

    def create(self, validated_data):
        User = get_user_model()
        request = self.context.get("request")
        company_id = self.context.get("company_id")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            with transaction.atomic():
                invite_data = {
                    'email': validated_data['email'],
                    'company_id': company_id,
                    'is_admin': validated_data.pop('is_admin'),
                    'role': validated_data.pop('role', None)
                }
                if 'username' not in validated_data.keys():
                    validated_data['username'] = get_random_string(25)
                if 'password' not in validated_data.keys():
                    validated_data['password'] = User.objects.make_random_password()
                User.objects.create_user(**validated_data)
                obj = InviteToCompany(**invite_data)
                obj.save()
                return obj
        return None
