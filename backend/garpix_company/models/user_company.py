from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _

from garpix_company.models.user_role import get_company_role_model

User = get_user_model()


class ActiveManager(Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_blocked=False)


class UserCompany(models.Model):
    """
    Модель участников. Связка между компанией и пользователем.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_companies', verbose_name=_('Пользователь'))
    company = models.ForeignKey(settings.GARPIX_COMPANY_MODEL, related_name='user_companies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата/время создания"))
    is_blocked = models.BooleanField(default=False, verbose_name=_("Заблокирован администратором компании"))
    role = models.ForeignKey(settings.GARPIX_COMPANY_ROLE_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name=_('Роль в компании'))

    objects = Manager()
    active_objects = ActiveManager()

    class Meta:
        unique_together = ("user", "company")
        verbose_name = _('Пользователь компании')
        verbose_name_plural = _('Пользователи компании')

    def block(self):
        """
        Заблокировать участника в компании
        :return: (bool, str)
        """
        if self.company.owner == self.user:
            return False, _('Нельзя заблокировать владельца компании')
        self.is_blocked = True
        self.save()
        return True, None

    def unblock(self):
        """
        Разблокировать участника в компании
        :return: (bool, str)
        """
        self.is_blocked = False
        self.save()
        return True, None

    def kick(self):
        """
        Удалить участника в компании
        :return: (bool, str)
        """
        if self.company.owner == self.user:
            return False, _('Нельзя удалить владельца компании')
        self.delete()
        return True, None

    def change_role(self, role):
        """
        Сменить роль участника в компании
        :return: (bool, str)
        """
        CompanyRole = get_company_role_model()
        if self.company.owner == self.user:
            return False, _('Нельзя сменить роль владельца компании')
        if role == CompanyRole.get_admin_role():
            return False, _('Нельзя сделать пользователя владельцем. Воспользуйтесь функционалом смены владельца')
        self.role = role
        self.save()
        return True, None
