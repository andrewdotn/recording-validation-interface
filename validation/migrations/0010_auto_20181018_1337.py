# Generated by Django 2.1.2 on 2018-10-18 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("validation", "0009_auto_20181018_1322")]

    operations = [
        migrations.AlterField(
            model_name="recordingsession",
            name="location",
            field=models.CharField(
                blank=True,
                choices=[("DS", "DS"), ("US", "US"), ("KCH", "KCH"), ("OFF", "OFF")],
                default="",
                help_text="The location of the recordings. May be empty.",
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="recordingsession",
            name="time_of_day",
            field=models.CharField(
                blank=True,
                choices=[("AM", "AM"), ("PM", "PM")],
                default="",
                help_text="The time of day the session occured. May be empty.",
                max_length=2,
            ),
        ),
    ]
