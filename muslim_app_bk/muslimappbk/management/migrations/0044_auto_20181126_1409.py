# Generated by Django 2.1.2 on 2018-11-26 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0043_auto_20181125_2148'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videoalbum',
            options={'ordering': ['-upload_time']},
        ),
        migrations.AddField(
            model_name='videoalbum',
            name='remark',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Remark'),
        ),
    ]
