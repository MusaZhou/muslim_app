# Generated by Django 2.1.2 on 2018-11-20 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0038_auto_20181120_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspiredvideo',
            name='screenshot',
        ),
    ]
