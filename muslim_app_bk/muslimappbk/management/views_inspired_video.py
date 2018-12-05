from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View
from management.models import InspiredVideo, VideoAlbum, Video, Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from management.forms import InspiredVideoForm, VideoAlbumForm
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.views.decorators.csrf import csrf_exempt, csrf_protect 
from django.conf import settings
from management.tasks import upload_file_task
from django.http import JsonResponse
from datetime import datetime
from django.core.files.storage import default_storage
from upyun.modules import sign
from upyun.modules.httpipe import cur_dt
import base64, time, json, logging, os, random, string
from django.db.models.fields import related

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')    
class InspiredVideoListView(View):
    def get(self, request, *args, **kwargs):
        video_list = InspiredVideo.objects.all()
        context = {'video_list': video_list}
        return render(request, 'management/inspired_video_table.html', context)
 
@method_decorator(login_required, name='dispatch')   
class InspiredVideoEditView(View):   
    def get_common_initial(self, request):
        return  {'upload_by': request.user}
    
    def append_initial_video(self, inspired_video, initial_data):
        latest_valid_video = inspired_video.latest_valid_video()
        if latest_valid_video is not None:
            initial_data['video_id'] = latest_valid_video.id
            initial_data['video_path'] = latest_valid_video.file.url
            
        thumbnail = inspired_video.thumbnail()
        if thumbnail is not None:
            initial_data['image_id'] = thumbnail.id
            
    def get(self, request, *args, **kwargs):
        initial_data = self.get_common_initial(request)
        if 'slug' in kwargs:
            slug = kwargs['slug']
            inspired_video = get_object_or_404(InspiredVideo, slug=slug)
            self.append_initial_video(inspired_video, initial_data)
            video_form = InspiredVideoForm(instance=inspired_video, initial=initial_data, user=request.user)
        else:
            slug = None
            video_form = InspiredVideoForm(initial=initial_data, user=request.user)
            
        context = {'video_form': video_form, 
                   'slug': slug}    
        return render(request, 'management/add_inspired_video.html', context)
    
    def post(self, request, *args, **kwargs):
        initial_data = self.get_common_initial(request)
        if 'slug' in kwargs:
            slug = kwargs['slug']
            inspired_video = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
            self.append_initial_video(inspired_video, initial_data)
            video_form = InspiredVideoForm(request.POST, instance=inspired_video, initial=initial_data, user=request.user)
        else:
            slug = None
            video_form = InspiredVideoForm(request.POST, initial=initial_data, user=request.user)
            
        if video_form.is_valid():
            inspired_video = video_form.save()
            
            # update relate video model
            video_id = video_form.cleaned_data['video_id']
            video = Video.objects.get(id=video_id)
            related_object = video.content_object
            if related_object is None:
                video.content_object = inspired_video
                video.save()
            
            # update related image model    
            image_id = video_form.cleaned_data['image_id']
            if image_id:
                image = Image.objects.get(id=image_id)
                related_object = image.content_object
                if related_object is None:
                    image.content_object = inspired_video
                    image.save()
            
            return redirect('management:inspired_video_list')
        
        context = {'video_form': video_form, 
                   'slug': slug}
        return render(request, 'management/add_inspired_video.html', context)
    
@method_decorator(login_required, name='dispatch')     
class InspiredVideoDeleteView(View):    
    def get(self, request, *args, **kwargs):
        inspired_video = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
        inspired_video.delete()
        return redirect('management:inspired_video_list')
    
@method_decorator(login_required, name='dispatch')     
class InspiredVideoDetailView(View):    
    def get(self, request, *args, **kwargs):
        inspired_video = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
        context = {'inspired_video': inspired_video}
        return render(request, 'management/inspired_video_detail.html', context)
    
@permission_required('management.can_approve_app')    
def update_inspired_video_status(request):
    if request.is_ajax():
        inspired_video_slug = request.POST['inspired_video_slug']
        status = request.POST['approve_status']
        remark = request.POST['remark']
        InspiredVideo.objects.filter(slug=inspired_video_slug).update(approve_status=status, 
                                                                            approved_time=datetime.now(), 
                                                                            approved_by=request.user, 
                                                                            remark=remark)
        return JsonResponse({'status': 1}, safe=False)

@method_decorator(login_required, name='dispatch')    
class VideoAlbumListView(View):
    def get(self, request, *args, **kwargs):
        album_list = VideoAlbum.objects.all()
        context = {'album_list': album_list}
        return render(request, 'management/video_album_list.html', context)
    
@method_decorator(login_required, name='dispatch')   
class VideoAlbumEditView(View):    
    def get_common_initial(self, request):
        return  {'upload_by': request.user}
    
    def append_initial_image(self, video_album, initial_data):
        image = video_album.get_image()
        if image:
            initial_data['image_id'] = image.id
            initial_data['image_path'] = image.thumbnail_picture.url
        
    def get(self, request, *args, **kwargs):
        initial_data = self.get_common_initial(request)
        if 'slug' in kwargs:
            slug = kwargs['slug']
            video_album = get_object_or_404(VideoAlbum, slug=slug)
            self.append_initial_image(video_album, initial_data)
            album_form = VideoAlbumForm(instance=video_album, initial=initial_data)
        else:
            slug = None
            album_form = VideoAlbumForm(initial=initial_data)
            
        context = {'album_form': album_form, 
                   'slug': slug}    
        return render(request, 'management/add_video_album.html', context)
    
    def post(self, request, *args, **kwargs):
        initial_data = self.get_common_initial(request)
        if 'slug' in kwargs:
            slug = kwargs['slug']
            video_album = get_object_or_404(VideoAlbum, slug=kwargs['slug'])
            self.append_initial_image(video_album, initial_data)
            album_form = VideoAlbumForm(request.POST, instance=video_album, initial=initial_data)
        else:
            slug = None
            album_form = VideoAlbumForm(request.POST, initial=initial_data)
            
        if album_form.is_valid():
            video_album = album_form.save()
            image_id = album_form.cleaned_data['image_id']
            if image_id:
                image = Image.objects.get(id=image_id)
                related_object = image.content_object
                if related_object is None:
                    image.content_object = video_album
                    image.save()
            return redirect('management:video_album_list')
        
        context = {'album_form': album_form, 
                   'slug': slug}
        return render(request, 'management/add_video_album.html', context)
    
@method_decorator(login_required, name='dispatch')     
class VideoAlbumDeleteView(View):    
    def get(self, request, *args, **kwargs):
        video_album = get_object_or_404(VideoAlbum, slug=kwargs['slug'])
        video_album.delete()
        return redirect('management:video_album_list')
    
@method_decorator(login_required, name='dispatch')     
class VideoAlbumDetailView(View):    
    def get(self, request, *args, **kwargs):
        video_album = get_object_or_404(VideoAlbum, slug=kwargs['slug'])
        context = {'video_album': video_album}
        return render(request, 'management/video_album_detail.html', context)
    
@permission_required('management.can_approve_app')    
def update_video_album_status(request):
    if request.is_ajax():
        video_album_slug = request.POST['video_album_slug']
        status = request.POST['approve_status']
        remark = request.POST['remark']
        VideoAlbum.objects.filter(slug=video_album_slug).update(approve_status=status, 
                                                                approved_time=datetime.now(), 
                                                                approved_by=request.user, 
                                                                remark=remark)
        return JsonResponse({'status': 1}, safe=False)