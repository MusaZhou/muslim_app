from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.views.generic import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group

# Create your views here.
   

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        userCreationForm = SignUpForm()
        context = {'userCreationForm': userCreationForm }
        return render(request, 'userauth/signup.html', context)
    
    def post(self, request, *args, **kwargs):
        userCreationForm = SignUpForm(request.POST)
        if userCreationForm.is_valid():
            user = userCreationForm.save()
            user_group = Group.objects.get(name='uploader')
            user.groups.add(user_group)
            user.refresh_from_db()
            user_profile = user.profile
            user_profile.date_of_birth = userCreationForm.cleaned_data['date_of_birth']
            user_profile.gender = userCreationForm.cleaned_data['gender']
            user_profile.avatar = request.FILES['avatar']
            raw_password = userCreationForm.cleaned_data['password1']
            user_profile.save()
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('management:app_table_basic')
        
        context = {'userCreationForm': userCreationForm }
        return render(request, 'userauth/signup.html', context)