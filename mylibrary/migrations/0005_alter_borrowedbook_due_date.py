# Generated by Django 5.1.7 on 2025-03-25 11:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mylibrary', '0004_alter_borrowedbook_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowedbook',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 8, 11, 4, 2, 693879, tzinfo=datetime.timezone.utc)),
        ),
    ]
