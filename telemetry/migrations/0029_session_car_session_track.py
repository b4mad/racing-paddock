# Generated by Django 5.1b1 on 2024-07-14 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("telemetry", "0028_segment_referencesegment"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="car",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="telemetry.car"
            ),
        ),
        migrations.AddField(
            model_name="session",
            name="track",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="telemetry.track"
            ),
        ),
    ]
