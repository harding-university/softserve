# Generated by Django 5.1.6 on 2025-04-07 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("softserve", "0002_alter_action_player_alter_game_event_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="token",
            field=models.TextField(blank=True),
        ),
    ]
