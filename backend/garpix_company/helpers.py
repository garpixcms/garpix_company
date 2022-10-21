from django.utils.translation import ugettext_lazy as _


class COMPANY_STATUS_ENUM:
    ACTIVE = 'active'
    BANNED = 'banned'
    DELETED = 'deleted'

    CHOICES = (
        (ACTIVE, _('Активна')),
        (BANNED, _('Забанена')),
        (DELETED, _('Удалена'))
    )


class CHOICES_INVITE_STATUS_ENUM:
    CREATED = 'created'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    CHOICES = (
        (CREATED, _('Создан')),
        (ACCEPTED, _('Принят')),
        (DECLINED, _('Отвергнут'))
    )
