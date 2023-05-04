from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition, can_proceed
from django.contrib.auth import get_user_model

from garpix_company.helpers import COMPANY_STATUS_ENUM
from garpix_company.managers.company import CompanyActiveManager

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps

from garpix_company.services.role_service import UserCompanyRoleService

User = get_user_model()


class AbstractCompany(models.Model):
    """
    Данные о компании.
    """

    COMPANY_STATUS = COMPANY_STATUS_ENUM

    title = models.CharField(max_length=255, verbose_name=_('Название'))
    full_title = models.CharField(max_length=255, verbose_name=_('Полное название'))
    inn = models.CharField(max_length=15, verbose_name=_('ИНН'))
    ogrn = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('ОГРН'))
    kpp = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("КПП"))
    bank_title = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Наименование банка"))
    bic = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("БИК банка"))
    schet = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Номер счета"))
    korschet = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Кор. счет"))
    ur_address = models.CharField(max_length=300, verbose_name=_("Юридический адрес"))
    fact_address = models.CharField(max_length=300, verbose_name=_("Фактический адрес"))
    status = FSMField(default=COMPANY_STATUS.ACTIVE, choices=COMPANY_STATUS.CHOICES, verbose_name=_('Статус'))
    participants = models.ManyToManyField(User, through='garpix_company.UserCompany',
                                          verbose_name=_('Участники компании'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата изменения'))
    objects = models.Manager()
    active_objects = CompanyActiveManager()

    class Meta:
        verbose_name = _('Компания')
        verbose_name_plural = _('Компании')
        ordering = ['-id']
        abstract = True

    @transition(field=status, source=COMPANY_STATUS.BANNED, target=COMPANY_STATUS.ACTIVE)
    def comp_active(self):
        pass

    @transition(field=status, source=COMPANY_STATUS.ACTIVE, target=COMPANY_STATUS.BANNED)
    def comp_banned(self):
        pass

    @transition(field=status, source=[COMPANY_STATUS.ACTIVE, COMPANY_STATUS.BANNED], target=COMPANY_STATUS.DELETED)
    def comp_deleted(self):
        pass

    @property
    def can_banned(self):
        return can_proceed(self.comp_banned)

    @property
    def can_deleted(self):
        return can_proceed(self.comp_deleted)

    @property
    def can_active(self):
        return can_proceed(self.comp_active)

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        self.comp_deleted()
        self.save()

    def hard_delete(self):
        super().delete()

    def change_owner(self, data, current_user):
        from .user_company import UserCompany
        company_role_service = UserCompanyRoleService()

        new_owner_id = data.get('new_owner')
        if self.owner != current_user:
            return False, _('Действие доступно только для владельца компании')
        try:
            user_company = UserCompany.objects.get(company=self, pk=int(new_owner_id))
            if self.owner == user_company.user:
                return False, _('Пользователь с указанным id уже является владельцем компании')
            if user_company.is_blocked:
                return False, _('Нельзя сделать владельцем заблокированного пользователя')
            admin_role = company_role_service.get_admin_role()
            owner_role = company_role_service.get_owner_role()

            new_role = data.get('role', admin_role)
            stay_in_company = data.get('stay_in_company', True)

            if stay_in_company:
                UserCompany.objects.filter(company=self, user=current_user).update(role=new_role)
            else:
                UserCompany.objects.filter(company=self, user=current_user).delete()
            user_company.role = owner_role
            user_company.save()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Пользователь с указанным id не является сотрудником компании')

    @classmethod
    def check_user_companies_limit(cls, user):
        return True

    @classmethod
    def invite_confirmation_link(cls, token):
        return f'{settings.SITE_URL}invite/{token}'

    @property
    def owner(self):
        company_role_service = UserCompanyRoleService()
        user_model_instance = self.user_companies.filter(role=company_role_service.get_owner_role()).first()
        if user_model_instance:
            return user_model_instance.user
        return None


def get_company_model():
    """
    Return the Company model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.GARPIX_COMPANY_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("GARPIX_COMPANY_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "GARPIX_COMPANY_MODEL refers to model '%s' that has not been installed" % settings.GARPIX_COMPANY_MODEL
        )
