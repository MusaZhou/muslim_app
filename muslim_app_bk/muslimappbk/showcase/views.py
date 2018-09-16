from django.shortcuts import render, get_object_or_404
from management.models import MobileApp

# Create your views here.
def blog_template(request):
    return render(request, 'showcase/blog_template.html')

def dashboard_template(request):
    return render(request, 'showcase/dashboard_template.html')

def carousel_template(request):
    return render(request, 'showcase/carousel_template.html')

def album_template(request):
    return render(request, 'showcase/album_template.html')

def index(request):
    return render(request, 'showcase/index.html')

def app(request, slug):
    mobile_app = get_object_or_404(MobileApp, slug=slug)
    app_version = mobile_app.latest_version()
    context = {'mobile_app': mobile_app, 'app_version': app_version}
    return render(request, 'showcase/app.html', context)