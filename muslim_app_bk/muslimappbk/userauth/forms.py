from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.models import User
from management.choices import GENDER_CHOICES
from django.forms.models import ModelForm
from management.models import Profile

class SignUpForm(UserCreationForm):  
    date_of_birth = forms.DateField(help_text='Format: YYYY-MM-DD', required=False)
    gender =forms.ChoiceField(choices=GENDER_CHOICES)
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2', 'gender', 'avatar')
        
class UserProfileForm(ModelForm):
    email = forms.EmailField(label="Email Address", required=False)
#     avatar = forms.ImageField(label="Avatar", required=False, error_messages={'invalid': "image files only"}, widget=forms.FileInput)
    class Meta:
        model = Profile
        fields = ('nick_name', 'gender', 'email', 'date_of_birth', 'avatar') 