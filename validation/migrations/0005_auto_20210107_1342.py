# Generated by Django 2.2.17 on 2021-01-07 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("validation", "0004_auto_20210107_1323"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalphrase",
            name="speaker",
        ),
        migrations.RemoveField(
            model_name="phrase",
            name="speaker",
        ),
    ]
