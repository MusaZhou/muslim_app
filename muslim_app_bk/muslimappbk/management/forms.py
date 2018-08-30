from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from models import MobileApp

class AddAppModelForm(ModelForm):
    # name, description, upload_by, video_url, upload_date, category_id,
    # avg_rate, comment_count, download_count, slug, active, status,
    # version_number, modified_date, approved_by, approved_date, approve_status, app_id
    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_url', 'category', 'version_number']
