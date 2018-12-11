from django.shortcuts import render, get_object_or_404
from management.models import MobileApp, Banner, AppCategory, PDFDoc, VideoAlbum, InspiredVideo
from taggit.models import Tag
from django.db.models import Q, F
import os

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

def disqus(request):
    return render(request, 'showcase/disqus.html')

def index_pdf(request):
    pdfdoc_list = PDFDoc.approved_pdf.all()
    author_list = {pdfdoc.author for pdfdoc in pdfdoc_list}
    year_list = {pdfdoc.publish_year.year for pdfdoc in pdfdoc_list}
    
    context = {'pdfdoc_list': pdfdoc_list, 'author_list': author_list, 'year_list':year_list}
    return render(request, 'showcase/index_pdf.html', context)  

def detail_pdf(request, slug):
    pdfdoc = get_object_or_404(PDFDoc.objects.prefetch_related('ratings', 'tags'), slug=slug)
    pdf_file_name_list = [os.path.split(pdf_file.file.path)[1] for pdf_file in pdfdoc.pdf_files.all()]
    context = {'pdfdoc': pdfdoc, 'pdf_file_name_list': pdf_file_name_list}
    return render(request, 'showcase/pdf.html', context)

def index_inspired_video(request):
    # for temporary, need filter album with approved value
    albums = VideoAlbum.objects.all()
    tags = Tag.objects.all()
    context = {'albums': albums, 'tags': tags}
    return render(request, 'showcase/index_inspired_video.html', context)

def detail_inspired_video(request, slug):
    inspired_video = get_object_or_404(InspiredVideo.shown_videos.prefetch_related('ratings', 'tags'), slug=slug)
    album = inspired_video.album
    if album:
        related_video_list = album.album_videos.exclude(Q(slug=inspired_video.slug) | Q(is_removed=1))
    else:
        tags = inspired_video.tags.all()
        related_video_list = InspiredVideo.shown_videos.filter(tags__id__in=tags.values_list('id', flat=True)).exclude(id=inspired_video.id)
    context = {'inspired_video': inspired_video, 'related_video_list': related_video_list}
    return render(request, 'showcase/detail_inspired_video.html', context)