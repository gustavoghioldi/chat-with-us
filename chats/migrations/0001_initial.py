# Generated by Django 5.2.1 on 2025-05-12 02:28

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("agents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatModel",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "session_id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("content", models.JSONField(blank=True)),
                (
                    "agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="agents.agentmodel",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
