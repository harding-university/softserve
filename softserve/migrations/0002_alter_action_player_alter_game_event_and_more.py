# Generated by Django 5.1.6 on 2025-03-22 21:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("softserve", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="action",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="softserve.gameplayer"
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="softserve.event"
            ),
        ),
        migrations.AlterField(
            model_name="gameplayer",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="softserve.player"
            ),
        ),
    ]
