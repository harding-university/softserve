# Generated by Django 5.1.6 on 2025-04-09 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("softserve", "0003_player_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="name",
            field=models.TextField(unique=True),
        ),
    ]
