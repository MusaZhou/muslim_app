# Generated by Django 2.1 on 2018-08-29 03:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.CharField(max_length=10)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('approve_status', models.CharField(choices=[('new', 'new'), ('approved', 'approved'), ('rejected', 'rejected')], default='new', max_length=10)),
                ('approved_time', models.DateTimeField(null=True)),
                ('active_status', models.CharField(choices=[('active', 'active'), ('inactive', 'inactive')], default='active', max_length=10)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('approve_status', models.CharField(choices=[('new', 'new'), ('approved', 'approved'), ('rejected', 'rejected')], default='new', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('rate', models.PositiveSmallIntegerField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('approve_status', models.CharField(choices=[('new', 'new'), ('approved', 'approved'), ('rejected', 'rejected')], default='new', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='MobileApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('description', models.TextField()),
                ('video_url', models.URLField(null=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('avg_rate', models.DecimalField(decimal_places=1, max_digits=2, null=True)),
                ('comment_count', models.PositiveIntegerField(null=True)),
                ('download_count', models.PositiveIntegerField(null=True)),
                ('slug', models.SlugField(unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.AppCategory')),
                ('upload_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50)),
                ('gender', models.CharField(choices=[('male', '男'), ('female', '女')], default='male', max_length=10)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, height_field=50, upload_to='avatar/%Y/%m/%d/', width_field=50)),
                ('wechatid', models.CharField(blank=True, db_index=True, max_length=100)),
                ('weiboid', models.CharField(blank=True, db_index=True, max_length=100)),
                ('qqid', models.CharField(blank=True, db_index=True, max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='evaluation',
            name='app',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.MobileApp'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='approved_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checked_evaluations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_evaluations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='app',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.MobileApp'),
        ),
        migrations.AddField(
            model_name='comment',
            name='approved_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checked_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='evluation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Evaluation'),
        ),
        migrations.AddField(
            model_name='appversion',
            name='mobileapp',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.MobileApp'),
        ),
    ]
