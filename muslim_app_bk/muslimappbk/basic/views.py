from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import logging
from django.core.mail import send_mail
from management.models import Image

logger = logging.getLogger(__name__)

# Create your views here.
def page_404(request):
    return render(request, 'management/404.html')

def page_500(request):
    return render(request, 'management/500.html')

def datatable(request):
    return render(request, 'management/datatable.html')

def forms(request):
    return render(request, 'management/forms.html')

def index(request):
    return render(request, 'management/index.html')

def signin(request):
    return render(request, 'management/signin.html')

def signup(request):
    return render(request, 'management/signup.html')

def others(request, file):
    # print('what is requesting is :' + characters)
    return redirect(settings.STATIC_URL + 'management/' + file)
#     return redirect(settings.STATIC_URL + file)

def customLogger(request):
    logger.debug('test logger')
    return HttpResponse(__name__)

def ui(request):
    return render(request, 'management/ui.html')

def email(request):
    return HttpResponse(send_mail('test', 'test from muslimapp', 'admin@muslimapp.cn', ['admin@muslimapp.cn','musazhou@gmail.com'], fail_silently=True))

def test(request):
#     profile = request.user.profile    
# #     logger.debug(pro)
    image = Image.objects.get(id=1)
    logger.debug('image width:' + image.picture.width)
    logger.debug('image height:' + image.picture.height)
    return JsonResponse({'height': image.height, 'width': image.width})