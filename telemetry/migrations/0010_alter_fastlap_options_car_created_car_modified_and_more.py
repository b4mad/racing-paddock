# Generated by Django 4.2.3 on 2023-07-04 16:27

import django.utils.timezone
import model_utils.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("telemetry", "0009_coach_fast_lap_coach_track_walk"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fastlap",
            options={"ordering": ["game", "car", "track"]},
        ),
        migrations.AddField(
            model_name="car",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="car",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="coach",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="coach",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="driver",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="driver",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="fastlap",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="fastlap",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="fastlapsegment",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="fastlapsegment",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="lap",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="lap",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="session",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="session",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="sessiontype",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="sessiontype",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
        migrations.AddField(
            model_name="track",
            name="created",
            field=model_utils.fields.AutoCreatedField(
                default=django.utils.timezone.now, editable=False, verbose_name="created"
            ),
        ),
        migrations.AddField(
            model_name="track",
            name="modified",
            field=model_utils.fields.AutoLastModifiedField(
                default=django.utils.timezone.now, editable=False, verbose_name="modified"
            ),
        ),
    ]
