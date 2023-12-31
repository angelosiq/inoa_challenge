# Generated by Django 4.2.4 on 2023-08-11 19:22

from django.db import migrations


def create_intervals(apps, schema_editor):
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")
    IntervalSchedule.objects.bulk_create(
        [
            IntervalSchedule(every=1, period="minutes"),
            IntervalSchedule(every=5, period="minutes"),
            IntervalSchedule(every=10, period="minutes"),
            IntervalSchedule(every=30, period="minutes"),
            IntervalSchedule(every=60, period="minutes"),
            IntervalSchedule(every=90, period="minutes"),
            IntervalSchedule(every=120, period="minutes"),
        ]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_intervals),
    ]
