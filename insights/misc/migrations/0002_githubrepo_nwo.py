# Generated by Django 3.1 on 2020-08-31 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("misc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="githubrepo",
            name="nwo",
            field=models.CharField(default="", max_length=200),
        ),
    ]
