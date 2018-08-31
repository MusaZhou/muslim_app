from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField
from models import MobileApp
from django.core import validators

class AddAppModelForm(ModelForm):
    # name, description, upload_by, video_url, upload_date, category_id,
    # avg_rate, comment_count, download_count, slug, active, status, tags
    # version_number, modified_date, approved_by, approved_date, approve_status, app_id
    version_number = CharField(max_length=10, validators=[validators.RegexValidator("*[a-zA-Z0-9\.]")])

    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_url', 'category', 'tags']
