# Generated by Django 2.2.20 on 2021-04-29 22:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("validation", "0013_auto_20210428_1551"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalrecording",
            name="status",
        ),
        migrations.RemoveField(
            model_name="issue",
            name="modified_by",
        ),
        migrations.RemoveField(
            model_name="issue",
            name="modified_on",
        ),
        migrations.RemoveField(
            model_name="recording",
            name="status",
        ),
        migrations.AddField(
            model_name="status",
            name="recording",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="validation.Recording",
            ),
        ),
        migrations.AlterField(
            model_name="issue",
            name="comment",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The comment left by the validator",
                max_length=1024,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="issue",
            name="created_on",
            field=models.DateField(help_text="When was this issue filed?"),
        ),
        migrations.AlterField(
            model_name="issue",
            name="suggested_cree",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The Cree spelling suggested by the validator",
                max_length=1024,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="issue",
            name="suggested_english",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The English spelling suggested by the validator",
                max_length=1024,
            ),
            preserve_default=False,
        ),
    ]
