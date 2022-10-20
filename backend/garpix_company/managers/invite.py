from django.db import models

from garpix_company.helpers import CHOICES_INVITE_STATUS


class CreatedInviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=CHOICES_INVITE_STATUS.CREATED)
