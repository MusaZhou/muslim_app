# Generated by Django 2.1.1 on 2018-09-09 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_auto_20180909_0300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileapp',
            name='active_status',
            field=models.BooleanField(default=False),
        ),
    ]
