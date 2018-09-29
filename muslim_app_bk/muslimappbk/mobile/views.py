from django.shortcuts import render, get_object_or_404
from management.models import MobileApp, Banner, AppCategory

# Create your views here.
def blog_template(request):
    return render(request, 'mobile/blog_template.html')

def dashboard_template(request):
    return render(request, 'mobile/dashboard_template.html')

def carousel_template(request):
    return render(request, 'mobile/carousel_template.html')

def album_template(request):
    return render(request, 'mobile/album_template.html')

def index(request):
    banner_list = Banner.objects.all()
    category_list = AppCategory.objects.all()
    context = {'banner_list': banner_list, 'category_list': category_list}
    return render(request, 'mobile/index.html', context)

def app(request, slug):
    mobile_app = get_object_or_404(MobileApp, slug=slug)
    app_version = mobile_app.latest_version()
    context = {'mobile_app': mobile_app, 'app_version': app_version}
    return render(request, 'mobile/app.html', context)
