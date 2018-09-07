from django import forms
from django.forms import ModelForm
from management.models import MobileApp, AppVersion


class AddAppModelForm(ModelForm):
    imgIds = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'imgIds'}))

    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_url', 'category', 'tags', 'slug']

class AddAppVersionModelForm(ModelForm):

    class Meta:
        model = AppVersion
        fields = ['version_number', 'whats_new', 'apk']
        

