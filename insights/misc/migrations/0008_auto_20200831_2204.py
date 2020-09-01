# Generated by Django 3.1 on 2020-08-31 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("misc", "0007_auto_20200831_2135"),
    ]

    operations = [
        migrations.AlterField(
            model_name="run",
            name="status",
            field=models.TextField(default="", max_length=200),
        ),
        migrations.CreateModel(
            name="Artifact",
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
                ("artifact_id", models.IntegerField()),
                ("created_at", models.DateTimeField(null=True)),
                ("size_in_bytes", models.IntegerField()),
                ("name", models.TextField(default=True, max_length=200)),
                ("expired", models.TextField(default=True, max_length=200)),
                ("download", models.URLField()),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="misc.run"
                    ),
                ),
            ],
        ),
    ]
