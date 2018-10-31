# Generated by Django 2.1.2 on 2018-10-31 06:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0029_pdfdoc_pdf_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='pdf', validators=[django.core.validators.FileExtensionValidator(['pdf'])], verbose_name='PDF File')),
            ],
        ),
        migrations.RemoveField(
            model_name='pdfdoc',
            name='pdf_file',
        ),
        migrations.AddField(
            model_name='pdffile',
            name='pdf_doc',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pdf', to='management.PDFDoc'),
        ),
    ]
