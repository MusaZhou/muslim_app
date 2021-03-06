# Generated by Django 2.1.2 on 2018-12-06 10:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0046_auto_20181127_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='apkfile',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appcategory',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appversion',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='banner',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='download',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='image',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inspiredvideo',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mobileapp',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pdfdoc',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='video',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='banners', verbose_name='Banner Image'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='link',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='inspiredvideo',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inspiredvideo_approved', to=settings.AUTH_USER_MODEL, verbose_name='Approved By'),
        ),
        migrations.AlterField(
            model_name='inspiredvideo',
            name='upload_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inspiredvideo_uploaded', to=settings.AUTH_USER_MODEL, verbose_name='Uploader'),
        ),
        migrations.AlterField(
            model_name='pdfdoc',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pdfdoc_approved', to=settings.AUTH_USER_MODEL, verbose_name='Approved By'),
        ),
        migrations.AlterField(
            model_name='pdfdoc',
            name='upload_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pdfdoc_uploaded', to=settings.AUTH_USER_MODEL, verbose_name='Uploader'),
        ),
        migrations.AlterField(
            model_name='videoalbum',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videoalbum_approved', to=settings.AUTH_USER_MODEL, verbose_name='Approved By'),
        ),
        migrations.AlterField(
            model_name='videoalbum',
            name='upload_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videoalbum_uploaded', to=settings.AUTH_USER_MODEL, verbose_name='Uploader'),
        ),
    ]
