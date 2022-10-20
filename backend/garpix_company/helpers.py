from django.utils.translation import ugettext_lazy as _


class COMPANY_STATUS:
    ACTIVE = 'active'
    BANNED = 'banned'
    DELETED = 'deleted'

    CHOICES = (
        (ACTIVE, _('Активна')),
        (BANNED, _('Забанена')),
        (DELETED, _('Удалена'))
    )


class CHOICES_INVITE_STATUS:
    CREATED = 'created'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    CHOICES = (
        (CREATED, 'Создан'),
        (ACCEPTED, 'Принят'),
        (DECLINED, 'Отвергнут')
    )
