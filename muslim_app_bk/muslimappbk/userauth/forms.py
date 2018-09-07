from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):  
    GENDER_CHOICES = (('male', '男'), ('female', '女'))
      
    date_of_birth = forms.DateField(help_text='Format: YYYY-MM-DD', required=False)
    gender =forms.ChoiceField(choices=GENDER_CHOICES)
    avatar = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2', 'gender', 'avatar')