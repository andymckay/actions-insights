# Generated by Django 3.1.1 on 2020-09-01 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0011_auto_20200901_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='elapsed',
            field=models.DurationField(null=True),
        ),
    ]
