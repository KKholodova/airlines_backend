# Generated by Django 4.2.7 on 2025-02-11 01:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="qr",
            field=models.TextField(blank=True, null=True),
        ),
    ]
