from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from .forms import SignUpForm
from django.views.generic import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.contrib.auth import logout

# Create your views here.
   

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        userCreationForm = SignUpForm()
        context = {'userCreationForm': userCreationForm }
        return render(request, 'userauth/signup.html', context)
    
    def post(self, request, *args, **kwargs):
        userCreationForm = SignUpForm(request.POST)
        if userCreationForm.is_valid():
            user = userCreationForm.save(False)
            user.is_active = False
            user.save()
            user_group = Group.objects.get(name='uploader')
            user.groups.add(user_group)
            user.refresh_from_db()
            user_profile = user.profile
            user_profile.date_of_birth = userCreationForm.cleaned_data['date_of_birth']
            user_profile.gender = userCreationForm.cleaned_data['gender']
            avatar = request.POST.get('avatar', False)
            if avatar:
                user_profile.avatar = avatar
            user_profile.save()
            
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('userauth/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return HttpResponse('Your activation letter has been sent, please check your email')
        
        context = {'userCreationForm': userCreationForm }
        return render(request, 'userauth/signup.html', context)
    
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('management:app_table_basic')
    else:
        return HttpResponse('The confirmation link was invalid, possibly because it has already been used.')

class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
    