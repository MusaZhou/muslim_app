# Generated by Django 2.1.2 on 2018-11-26 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0044_auto_20181126_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspiredvideo',
            name='download_count',
        ),
        migrations.AddField(
            model_name='inspiredvideo',
            name='view_count',
            field=models.PositiveIntegerField(default=0, verbose_name='View Count'),
        ),
        migrations.AlterField(
            model_name='videoalbum',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='videoalbum',
            name='title',
            field=models.CharField(max_length=100, unique=True, verbose_name='Title'),
        ),
    ]
