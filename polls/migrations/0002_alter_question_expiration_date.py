# Generated by Django 5.1.2 on 2024-10-24 04:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 31, 11, 35, 4, 62826), verbose_name='Дата окончания'),
        ),
    ]
