from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.apps import apps as django_apps


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

    def clean(self):
        super().clean()
        if self.role_type in [self.ROLE_TYPE.ADMIN, self.ROLE_TYPE.OWNER]:
            if self.__class__.objects.filter(role_type=self.role_type).exists():
                raise ValidationError({'role_type': _(f'Недопустимо создание более одной роли с типом {dict(self.ROLE_TYPE.choices)[self.role_type]}')})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Роль в компании')
        verbose_name_plural = _('Роли в компаниях')
        ordering = ['-id']
        abstract = True


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
