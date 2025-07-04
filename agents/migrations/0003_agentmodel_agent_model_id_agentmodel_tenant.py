# Generated by Django 4.2.21 on 2025-06-05 18:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0001_initial"),
        ("agents", "0002_agentmodel_knoledge_text_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="agentmodel",
            name="agent_model_id",
            field=models.CharField(
                blank=True,
                help_text="ID del modelo de IA utilizado por el agente",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="agentmodel",
            name="tenant",
            field=models.ForeignKey(
                blank=True,
                default=None,
                help_text="Inquilino al que pertenece el agente",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="agents",
                to="tenants.tenantmodel",
            ),
        ),
    ]
