from django import forms
from django.forms import ModelForm
from management.models import MobileApp, AppVersion, Banner
from django.forms import ModelChoiceField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Tag


class AddAppModelForm(ModelForm):
    imgIds = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'imgIds'}))
    video_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'video_id'}))
#     tags = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Tag.objects.all())
    
    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_id', 'tags', 'category', 'slug', 'icon', 'developer']

class AddAppVersionModelForm(ModelForm):
    apk_id = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden', 'id':'apk_id'}))
    
    class Meta:
        model = AppVersion
        fields = ['version_number', 'whats_new', 'apk_id', 'translator', 'android_version']

class ModelChoiceFieldBeta(ModelChoiceField):
    
    def to_python(self, value):
        if value in self.empty_values:
            return None
        return value 
         
class BannerForm(ModelForm):
    app_list = ModelChoiceFieldBeta(queryset=MobileApp.objects.all(), 
                                    to_field_name='userLink', 
                                    label=_('Select Application as the Link'),
                                    required=False)
    
    class Meta:
        model = Banner
        fields = ['title', 'description', 'image', 'link']
        
    def clean_app_list(self):
        data = self.cleaned_data['app_list']
        return data
    

        

