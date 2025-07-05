from django.utils.translation import gettext_lazy as _
from django.db import models

class TransactionType(models.TextChoices):
    CONSUME = "consume", _("Consume")
    RECHARGE = "recharge", _("Recharge")
    RESET = "reset", _("Reset")
    ADJUST = "adjust", _("Adjust")