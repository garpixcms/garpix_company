from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from garpix_company.models.user_role import get_company_role_model

User = get_user_model()


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

    class Meta:
        unique_together = ("user", "company")
        verbose_name = _('Пользователь компании')
        verbose_name_plural = _('Пользователи компании')

    def block(self, by_user_id):
        """
        Заблокировать участника в компании
        :param by_user_id: ID пользователя, который хочет заблокировать
        :return:
        """
        CompanyRole = get_company_role_model()
        if self.company.owner == self.user:
            return False, _('Нельзя заблокировать владельца компании')
        if self.role == CompanyRole.get_admin_role():
            return False, _('Нельзя заблокировать администратора компании')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), role=CompanyRole.get_admin_role())
            self.is_blocked = True
            self.save()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')

    def unblock(self, by_user_id):
        """
        Разблокировать участника в компании
        :param by_user_id: ID пользователя, который хочет разблокировать
        :return:
        """
        try:
            CompanyRole = get_company_role_model()
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), role=CompanyRole.get_admin_role())
            self.is_blocked = False
            self.save()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')

    def kick(self, by_user_id):
        """
        Удалить участника в компании
        :param by_user_id: ID пользователя, который хочет заблокировать
        :return:
        """
        CompanyRole = get_company_role_model()
        if self.company.owner == self.user:
            return False, _('Нельзя удалить владельца компании')
        if self.role == CompanyRole.get_admin_role():
            return False, _('Нельзя удалить администратора компании')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), role=CompanyRole.get_admin_role())
            self.delete()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')

    def change_role(self, by_user_id, role):
        """
        Сменить роль участника в компании
        :param by_user_id: ID пользователя, который хочет заблокировать
        :return:
        """
        CompanyRole = get_company_role_model()
        if self.company.owner == self.user:
            return False, _('Нельзя сменить роль владельца компании')
        if role == CompanyRole.get_admin_role():
            return False, _('Нельзя сделать пользователя владельцем. Воспользуйтесь функционалом смены владельца')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), role=CompanyRole.get_admin_role())
            self.role = role
            self.save()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')
