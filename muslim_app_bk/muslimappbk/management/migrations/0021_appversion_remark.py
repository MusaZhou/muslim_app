# Generated by Django 2.1.1 on 2018-10-06 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0020_auto_20181004_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='appversion',
            name='remark',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Remark'),
        ),
    ]
