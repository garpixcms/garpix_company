from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction
from django_fsm import FSMField, transition, can_proceed
from garpix_notify.models import Notify
from garpix_utils.string import get_random_string

from garpix_company.helpers import CHOICES_INVITE_STATUS_ENUM
from garpix_company.managers.invite import CreatedInviteManager
from garpix_company.models.company import get_company_model
from garpix_company.models.user_company import get_user_company_model

User = get_user_model()
UserCompany = get_user_company_model()


class InviteToCompany(models.Model):
    CHOICES_INVITE_STATUS = CHOICES_INVITE_STATUS_ENUM

    company = models.ForeignKey(settings.GARPIX_COMPANY_MODEL, on_delete=models.CASCADE, verbose_name=_('Компания'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('E-mail инвайта'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата/время создания"))
    token = models.CharField(max_length=16, verbose_name=_("Код подтверждения добавления"))
    status = FSMField(choices=CHOICES_INVITE_STATUS.CHOICES, default=CHOICES_INVITE_STATUS.CREATED,
                      verbose_name=_("Статус инвайта"))
    role = models.ForeignKey(settings.GARPIX_COMPANY_ROLE_MODEL, on_delete=models.CASCADE,
                             verbose_name=_('Роль в компании'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Пользователь'))
    objects = models.Manager()
    created_objects = CreatedInviteManager()

    class Meta:
        verbose_name = _('Инвайт в компанию')
        verbose_name_plural = _('Инвайты в компании')
        ordering = ['-id']

    @transition(field=status, source=CHOICES_INVITE_STATUS.CREATED, target=CHOICES_INVITE_STATUS.ACCEPTED)
    def _in_accept(self, user):

        UserCompany.objects.create(
            company=self.company,
            user=user,
            role=self.role
        )

    @transition(field=status, source=CHOICES_INVITE_STATUS.CREATED, target=CHOICES_INVITE_STATUS.DECLINED)
    def _in_decline(self):
        pass

    @property
    def can_decline(self):
        return can_proceed(self._in_decline)

    @property
    def can_accept(self):
        return can_proceed(self._in_accept)

    def accept(self):
        """
        Принятие инвайта в компанию
        :return:
        """
        try:
            with transaction.atomic():
                user = self.user if self.user else User.objects.get(email=self.email)
                self._in_accept(user)
                self.save()
            return True, None
        except User.DoesNotExist:
            return False, _('Пользователь с таким email не зарегистрирован')
        except IntegrityError:
            return False, _('Не удалось принять приглашение. Попробуйте позже')

    def decline(self):
        """
        Отвержение инвайта в компанию
        :return:
        """
        self._in_decline()
        self.save()

    def save(self, *args, **kwargs):
        Company = get_company_model()
        is_new = self.pk is None
        search_data = {'company': self.company}
        if self.user:
            search_data.update({'user': self.user})
        else:
            search_data.update({'email': self.email})
        self.__class__.objects.filter(**search_data).update(status=self.CHOICES_INVITE_STATUS.DECLINED)
        if is_new:
            self.token = get_random_string(16)
            email = self.email if self.email else self.user.email
            Notify.send(settings.NOTIFY_EVENT_INVITE_TO_COMPANY, {
                'invite_confirmation_link': Company.invite_confirmation_link(self.token),
                'company_title': str(self.company),
                'invite': self
            }, email=str(email))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Инвайт в компанию {str(self.company)} для {self.email}'
