from django.db import models

class TransactionDirectionType(models.TextChoices):
    IN = "IN"
    OUT = "OUT"