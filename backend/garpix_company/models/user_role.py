from django.db import models
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AbstractUserCompanyRole(models.Model):
    """
    Роли в компаниях.
    """

    class ROLE_TYPE(models.TextChoices):
        ADMIN = ('admin', 'Админ')
        OWNER = ('owner', 'Владелец')
        EMPLOYEE = ('employee', 'Сотрудник')

    title = models.CharField(max_length=255, verbose_name=_('Название'))
    role_type = models.CharField(max_length=128, choices=ROLE_TYPE.choices, default=ROLE_TYPE.EMPLOYEE,
                                 verbose_name=_('Тип'))

    class Meta:
        verbose_name = 'Роль в компании | User company role'
        verbose_name_plural = 'Роли в компаниях | User companies roles'
        ordering = ['-id']
        abstract = True

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        self._validate_role_type_unique()

    def _validate_role_type_unique(self):
        if self.role_type not in {self.ROLE_TYPE.ADMIN, self.ROLE_TYPE.OWNER}:
            return

        qs = self.__class__.objects.filter(role_type=self.role_type)

        if self.pk is not None:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError({'role_type': _(f'Недопустимо создание более одной роли с типом') + f' {self.role_type.label}'})


def get_company_role_model():
    """
    Return the UserCompanyRole model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.GARPIX_COMPANY_ROLE_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("GARPIX_COMPANY_ROLE_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "GARPIX_COMPANY_ROLE_MODEL refers to model '%s' that has not been installed" % settings.GARPIX_COMPANY_ROLE_MODEL
        )
