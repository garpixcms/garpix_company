from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserCompany(models.Model):
    """
    Модель участников. Связка между компанией и пользователем.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usercompany', verbose_name=_('Пользователь'))
    company = models.ForeignKey(settings.GARPIX_COMPANY_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата/время создания"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Администратор компании"))
    is_blocked = models.BooleanField(default=False, verbose_name=_("Заблокирован администратором компании"))
    role = models.ForeignKey(settings.GARPIX_COMPANY_ROLE_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name=_('Роль в компании'))

    class Meta:
        unique_together = ("user", "company")
        verbose_name = _('Пользователь компании')
        verbose_name_plural = _('Пользователи компании')

    def set_admin(self, by_user_id):
        if self.is_blocked:
            return False, _('Нельзя сделать администратором заблокированного пользователя')
        if self.is_admin:
            return False, _('Пользователь уже является администратором выбранной компании')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), is_admin=True)
            self.is_admin = True
            self.is_blocked = False
            self.save()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')

    def unset_admin(self, by_user_id):
        """
        Лишить себя админства нельзя, остальных можно из этой компании, если админ.
        :param by_user_id:
        :return:
        """
        try:
            by_user = UserCompany.objects.get(company=self.company, user_id=int(by_user_id), is_admin=True)
            if by_user.id != self.id:
                self.is_admin = False
                self.save()
                return True, None
            else:
                return False, _('Лишить себя админства нельзя')
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')

    def block(self, by_user_id):
        """
        Заблокировать участника в компании
        :param by_user_id: ID пользователя, который хочет заблокировать
        :return:
        """
        if self.company.owner == self.user:
            return False, _('Нельзя заблокировать владельца компании')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), is_admin=True)
            if not self.is_admin:
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
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), is_admin=True)
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
        if self.company.owner == self.user:
            return False, _('Нельзя удалить владельца компании')
        if self.is_admin:
            return False, _('Нельзя удалить администратора компании')
        try:
            UserCompany.objects.get(company=self.company, user_id=int(by_user_id), is_admin=True)
            self.delete()
            return True, None
        except UserCompany.DoesNotExist:
            return False, _('Действие доступно только для администратора компании')
