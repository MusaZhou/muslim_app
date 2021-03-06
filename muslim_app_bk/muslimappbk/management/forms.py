from django import forms
from django.forms import ModelForm
from management.models import MobileApp, AppVersion, Banner, PDFDoc,\
    InspiredVideo, VideoAlbum
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _
from taggit_labels.widgets import LabelWidget
from taggit.forms import TagField
from django.core.exceptions import ValidationError
import re
from datetime import date


class AddAppModelForm(ModelForm):
    imgIds = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'imgIds'}))
    video_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'video_url'}))
    tags = TagField(required=False, widget=LabelWidget)
    
    class Meta:
        model = MobileApp
        fields = ['name', 'description', 'video_url', 'tags', 'category', 'slug', 'icon', 'developer']

class AddAppVersionModelForm(ModelForm):
    apk_url = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden', 'id':'apk_url'}))
    mobile_app = forms.ModelChoiceField(required=False, queryset=MobileApp.objects.all())
    
    class Meta:
        model = AppVersion
        fields = ['version_number', 'whats_new', 'apk_url', 'translator', 'android_version', 'mobile_app']

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
    
    pdf_list = ModelChoiceFieldBeta(queryset=PDFDoc.objects.all(),
                                    to_field_name="user_link",
                                    label=_('Select PDF as the Link'),
                                    required=False)
    
    video_list = ModelChoiceFieldBeta(queryset=InspiredVideo.objects.all(),
                                    to_field_name="userLink",
                                    label=_('Select Inspired Video as the Link'),
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
    pdf_file_urls = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'type': 'hidden', 'id':'pdf_file_urls'}))
    publish_year = YearField(required=False)
    
    class Meta:
        model = PDFDoc
        fields = ['title', 'description', 'tags', 'slug', 'pdf_file_urls', 'upload_by', 'author', 'publish_year']
        
class InspiredVideoForm(ModelForm):
    video_id = forms.CharField(widget=forms.HiddenInput(attrs={'id':'video_id'}))
    image_id = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id':'image_id'}))
    tags = TagField(required=False, widget=LabelWidget)
    video_path = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = InspiredVideo
        fields = ['video_id', 'image_id', 'title', 'description', 'tags', 'slug', 'upload_by', 'album', 'video_path']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InspiredVideoForm, self).__init__(*args, **kwargs)
        
        if not user.has_perm('management.can_approve_app'):
            self.fields['album'].queryset = VideoAlbum.objects.filter(upload_by=user)

class VideoAlbumForm(ModelForm):
    image_id = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id':'image_id'}))
    image_path = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = VideoAlbum
        fields = ['image_id', 'title', 'description', 'slug', 'upload_by', 'image_path']
