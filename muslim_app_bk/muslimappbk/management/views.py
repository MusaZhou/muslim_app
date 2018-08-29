from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.
def page_404(request):
    return render(request, 'management/404.html')

def page_500(request):
    return render(request, 'management/500.html')

def datatable(request):
    return render(request, 'management/datatable.html')

def forms(request):
    return render(request, 'management/forms.html')

def signin(request):
    return render(request, 'management/signin.html')

def signup(request):
    return render(request, 'management/signup.html')

def others(request, characters):
    # print('what is requesting is :' + characters)
    return redirect(settings.STATIC_URL + request.resolver_match.namespace + '/' + characters)
