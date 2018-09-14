from django.shortcuts import render

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

def app(request):
    return render(request, 'showcase/app.html')