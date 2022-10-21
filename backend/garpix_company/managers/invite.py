from django.db import models

from garpix_company.helpers import CHOICES_INVITE_STATUS_ENUM


class CreatedInviteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=CHOICES_INVITE_STATUS_ENUM.CREATED)
