from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition, can_proceed
from django.contrib.auth import get_user_model

from garpix_company.helpers import COMPANY_STATUS_ENUM
from garpix_company.managers.company import CompanyActiveManager

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps


class AbstractUserCompanyRole(models.Model):
    """
    Роли в компаниях.
    """

    title = models.CharField(max_length=255, verbose_name=_('Название'))

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
