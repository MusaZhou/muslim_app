# Generated by Django 2.1.2 on 2018-11-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0037_auto_20181115_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspiredvideo',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='videoalbum',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='title'),
        ),
    ]
