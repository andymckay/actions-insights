# Generated by Django 3.1 on 2020-08-31 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("misc", "0004_auto_20200831_2120"),
    ]

    operations = [
        migrations.CreateModel(
            name="Run",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("run_id", models.IntegerField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("timing", models.IntegerField()),
                ("status", models.TextField(default="")),
                ("conclusion", models.TextField(default="", max_length=200)),
                (
                    "workflow",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="misc.workflow"
                    ),
                ),
            ],
        ),
    ]
