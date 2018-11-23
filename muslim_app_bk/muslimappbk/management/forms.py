from django import forms
from django.forms import ModelForm
from management.models import MobileApp, AppVersion, Banner, PDFDoc,\
    InspiredVideo
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _
from taggit_labels.widgets import LabelWidget
from taggit.forms import TagField
from django.core.exceptions import ValidationError
import re
from datetime import date


class AddAppModelForm(ModelForm):
    imgIds = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'imgIds'}))
    video_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'video_id'}))
    tags = TagField(required=False, widget=LabelWidget)
    
    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_id', 'tags', 'category', 'slug', 'icon', 'developer']

class AddAppVersionModelForm(ModelForm):
    apk_id = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden', 'id':'apk_id'}))
    mobile_app = forms.ModelChoiceField(required=False, queryset=MobileApp.objects.all())
    
    class Meta:
        model = AppVersion
        fields = ['version_number', 'whats_new', 'apk_id', 'translator', 'android_version', 'mobile_app']

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

class YearField(forms.DateField):
    def to_python(self, value):
        year_re = re.compile('^\d{4}$')
    
        if not year_re.match(str(value)):
            raise ValidationError('%s is not a valid year.' % value)
                                  
        return date(int(value), 1, 1)
    
    def prepare_value(self, value):
        if isinstance(value, date):
            return value.year
        return value
        
class PDFDocForm(ModelForm):
    tags = TagField(required=False, widget=LabelWidget)
    pdf_file_ids = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden', 'id':'pdf_file_ids'}))
    publish_year = YearField(required=False)
    
    class Meta:
        model = PDFDoc
        fields = ['title', 'description', 'tags', 'slug', 'pdf_file_ids', 'upload_by', 'author', 'publish_year']
        
class InspiredVideoForm(ModelForm):
    video_id = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id':'video_id'}))
    tags = TagField(required=False, widget=LabelWidget)
    policy = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id':'upyun_policy'}))
    authorization = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id':'upyun_authorization'}))
    video_path = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = InspiredVideo
        fields = ['video_id', 'title', 'description', 'tags', 'slug', 'upload_by', 'album', 'policy', 'authorization', 'video_path']
