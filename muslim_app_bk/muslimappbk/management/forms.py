from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField
from models import MobileApp, AppVersion
from django.core import validators

class AddAppModelForm(ModelForm):
    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_url', 'category', 'tags']

class AddAppVersionModelForm(ModelForm):
    class Meta:
        model = AppVersion
        fields = ['version_number']