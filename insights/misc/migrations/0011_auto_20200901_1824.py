# Generated by Django 3.1 on 2020-09-01 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("misc", "0010_repo_public"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artifact",
            name="expired",
            field=models.BooleanField(default=True),
        ),
    ]
