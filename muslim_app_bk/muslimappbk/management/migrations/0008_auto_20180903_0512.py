# Generated by Django 2.1.1 on 2018-09-03 05:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_auto_20180902_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appversion',
            name='approved_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appversion',
            name='mobile_app',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='management.MobileApp'),
        ),
        migrations.AlterField(
            model_name='appversion',
            name='version_number',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('[a-zA-Z0-9\\.]*')]),
        ),
    ]
