from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.models import User
from management.choices import GENDER_CHOICES
from django.forms.models import ModelForm
from management.models import Profile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

class SignUpForm(UserCreationForm):  
    date_of_birth = forms.DateField(help_text=_('Format: YYYY-MM-DD'), required=False)
    gender =forms.ChoiceField(choices=GENDER_CHOICES)
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2', 'gender', 'avatar')
        
    def clean_password2(self):
        password2 = super().clean_password2()
        password_validation.validate_password(
            self.cleaned_data['password2']
        )
        return password2 
        
class UserProfileForm(ModelForm):
    email = forms.EmailField(label=_("Email Address"), required=False)
#     avatar = forms.ImageField(label="Avatar", required=False, error_messages={'invalid': "image files only"}, widget=forms.FileInput)
    class Meta:
        model = Profile
        fields = ('nick_name', 'gender', 'email', 'date_of_birth', 'avatar') 