# Generated by Django 2.1.1 on 2018-09-21 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0015_auto_20180919_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mobileapp',
            name='avg_rate',
        ),
    ]
