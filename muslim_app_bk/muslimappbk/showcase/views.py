from django.shortcuts import render, get_object_or_404
from management.models import MobileApp, Banner, AppCategory
from django.db.models import Q

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
    banner_list = Banner.objects.all()
    category_list = AppCategory.objects.all()
    context = {'banner_list': banner_list, 'category_list': category_list}
    return render(request, 'showcase/index.html', context)

def app(request, slug):
    mobile_app = get_object_or_404(MobileApp.objects.prefetch_related('images', 'videos', 'ratings', 'tags'), slug=slug)
    app_version = mobile_app.latest_version()
    context = {'mobile_app': mobile_app, 'app_version': app_version}
    return render(request, 'showcase/app.html', context)

def search(request):
    search_word = request.POST.get('search_word', 'Quran')
    app_list = MobileApp.shown_apps.filter(Q(name__icontains=search_word)|\
                                           Q(description__icontains=search_word)|\
                                           Q(category__name__icontains=search_word))
    context = {'app_list': app_list}
    return render(request, 'showcase/search.html', context)
