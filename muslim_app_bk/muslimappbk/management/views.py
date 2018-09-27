from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from management.forms import AddAppModelForm, AddAppVersionModelForm, BannerForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from management.models import Image, MobileApp, AppVersion, Banner, Video,\
    ApkFile
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.core.paginator import Paginator, Page
from django.core.exceptions import ValidationError
from datetime import datetime
import logging, os, random, string
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
import requests
from management.tasks import upload_file_task

logger = logging.getLogger(__name__)
                
# Create your views here.
@login_required
def add_mobile_app(request):
    if request.method == 'POST':
        addAppModelForm = AddAppModelForm(request.POST, request.FILES)
        addAppVersionModelForm = AddAppVersionModelForm(request.POST, request.FILES)
        if addAppModelForm.is_valid()\
        and addAppVersionModelForm.is_valid():
            user = request.user
            newApp = addAppModelForm.save(commit=False)
            newApp.upload_by = user
            newApp.save()
            addAppModelForm.save_m2m()

            newAppVersion = addAppVersionModelForm.save(commit=False)
            newAppVersion.mobile_app = newApp
            try:
                newAppVersion.full_clean()
                newAppVersion.save()
                
                apk_id = addAppVersionModelForm.cleaned_data['apk_id']
                ApkFile.objects.filter(id=apk_id).update(app_version=newAppVersion)
    
                imgIds = addAppModelForm.cleaned_data['imgIds']
                logger.debug('imgIds:' + imgIds)
                if imgIds:
                    imgIds = imgIds.split(',')
                    for img in Image.objects.filter(id__in=imgIds):
                        img.content_object = newApp
                        img.save()
                
                video_id = addAppModelForm.cleaned_data['video_id']
                if video_id:
                    video = Video.objects.get(id=video_id)
                    video.content_object = newApp
                    video.save()
                    
                return redirect('management:app_table_basic')\
                     if user.has_perm('management.can_approve_app')\
                     else redirect('management:app_table_uploader')
            except ValidationError as error:
                addAppVersionModelForm.add_error(None, error)
                newApp.delete()
    else:
        addAppModelForm = AddAppModelForm()
        addAppVersionModelForm = AddAppVersionModelForm()
        
    logger.debug('app form errors:' + ','.join(addAppModelForm.errors))
    logger.debug('app version form errors:' + ','.join(addAppVersionModelForm.errors))  
    return render(request,
                  'management/add_mobile_app.html',
                    {'addAppModelForm': addAppModelForm,
                    'addAppVersionModelForm': addAppVersionModelForm})

class ImageFieldView(LoginRequiredMixin, View):
    def post(self, request):
        if request.is_ajax():
            files = request.FILES.getlist('images');
            # print('file count:'+ ',' + str(len(files)))
            imageIds = []
            for file in files:
                image = Image(picture=file)
                image.save()
                image_meta = requests.get(image.picture.url + '!/info')
                if image_meta.status_code == 200:
                    image_json = image_meta.json()
                    image.width = image_json['width']
                    image.height = image_json['height']
                    image.save()
                    
                imageIds.append(image.id)
            return JsonResponse(imageIds, safe=False)

class UpdateMobileAppView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug']);
        appImages = mobile_app.images.all()
        imgIds = []
        imgUrls = []
        for img in appImages:
            imgIds.append(str(img.id))
            imgUrls.append(img.picture.url)
            logger.debug('imgIds:' + str(imgIds))
            logger.debug('imgUrls:' + str(imgUrls))
        imgIds = ','.join(imgIds)
        
        video_id = None
        last_video = mobile_app.videos.last()
        if last_video is not None:
            video_id = last_video.id
        
        initial_data = {'imgIds': imgIds, 'video_id': video_id}
        updateAppModelForm = AddAppModelForm(instance=mobile_app, initial=initial_data)
        return render(request, 'management/update_mobile_app.html', {'updateAppModelForm': updateAppModelForm,
                                                                     'imgUrls': imgUrls})

    def post(self, request, *args, **kwargs):
        mobile_app = get_object_or_404(MobileApp, slug=kwargs['slug'])
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app)
        imgUrls = []
        video_id = None
        
        if updateAppModelForm.is_valid():
            mobile_app = updateAppModelForm.save()
            imgIds = updateAppModelForm.cleaned_data['imgIds']
            logger.debug('new imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
                update_app_images(imgIds, mobile_app)
                
            video_id = updateAppModelForm.cleaned_data['video_id']
            
            if video_id:
                video = Video.objects.get(id=video_id)
                if video.content_object is None:
                    video.content_object = mobile_app
                    video.save()
            
            return redirect('management:index')
        else:
            appImages = mobile_app.images.all()
            imgUrls = []
            for img in appImages:
                imgUrls.append(img.picture.url)
            
            last_video = mobile_app.videos().last()
            if last_video is not None:
                video_id = last_video.id
                
        return render(request, 'management/update_mobile_app.html', 
                          {'updateAppModelForm': updateAppModelForm,
                             'imgUrls': imgUrls,
                             'video_id': video_id})
            
class AppTableBasicView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    
    def get(self, request, *args, **kwargs):
        all_apps = MobileApp.objects.all()
        paginator = Paginator(all_apps, 5)
        page = request.GET.get('page')
        page_apps = paginator.get_page(page)
        
        return render(request, 'management/app_table_basic.html', {'page_apps': page_apps})

@method_decorator(login_required, name='dispatch')
class AddAppVersionView(View):
    def get(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug'])
        addAppVersionModelForm = AddAppVersionModelForm()
        appImages = mobile_app.images.all()
        imgIds = []
        imgUrls = []
        for img in appImages:
            imgIds.append(str(img.id))
            imgUrls.append(img.picture.url)
        imgIds = ','.join(imgIds)
        updateAppModelForm = AddAppModelForm(instance=mobile_app, initial={'imgIds': imgIds})
        return render(request,
                  'management/add_app_version.html',
                    {'addAppVersionModelForm': addAppVersionModelForm,
                     'updateAppModelForm': updateAppModelForm,
                     'imgUrls': imgUrls})
        
    def post(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug'])
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app)
        addAppVersionModelForm = AddAppVersionModelForm(request.POST, request.FILES)
        
        if updateAppModelForm.is_valid() and addAppVersionModelForm.is_valid():
            user = request.user
            new_app_version = addAppVersionModelForm.save(commit=False)
            new_app_version.upload_by = user
            new_app_version.mobile_app = mobile_app
            try:
                new_app_version.full_clean()
                mobile_app = updateAppModelForm.save()
                new_app_version.save()
                imgIds = updateAppModelForm.cleaned_data['imgIds']
                
                apk_id = addAppVersionModelForm.cleaned_data['apk_id']
                ApkFile.objects.filter(id=apk_id).update(app_version=new_app_version)
                
                if imgIds:
                    imgIds = imgIds.split(',')
                    update_app_images(imgIds, mobile_app)
                    
                return redirect('management:app_history', slug=mobile_app.slug)\
                     if user.has_perm('management.can_approve_app')\
                     else redirect('management:app_history_uploader', slug=mobile_app.slug)
        
            except ValidationError as error:
                addAppVersionModelForm.add_error(None, error)
            
        appImages = mobile_app.images.all()
        imgUrls = []
        for img in appImages:
            imgUrls.append(img.picture.url)
                
        return render(request,
              'management/add_app_version.html',
                {'addAppVersionModelForm': addAppVersionModelForm,
                 'updateAppModelForm': updateAppModelForm,
                 'imgUrls': imgUrls})
            
class AppHistoryView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    def get(self, request, *args, **kwargs):
        mobile_app = get_object_or_404(MobileApp, slug=kwargs['slug'])
        app_version_list = mobile_app.appversion_set.all()
        context = {'mobile_app': mobile_app, 'app_version_list': app_version_list}
        return render(request, 'management/app_history.html', context)
    
    def post(self, request, *args, **kwargs):
        pass

    
def update_app_images(imgIds, mobile_app):
    logger.debug('new imgIds:' + ','.join(imgIds))
    if imgIds:
        new_qs = Image.objects.filter(id__in=imgIds)
        old_qs = mobile_app.images.all()
        del_qs = old_qs.exclude(id__in=imgIds)
        # delete removed images
        del_qs.delete()

        for img in new_qs:
            # logger.debug('img id:' + str(img.id) + '\n content_object:' + str(img.content_object))
            if not img.content_object:
                img.content_object = mobile_app;
                img.save()

                
class VersionDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        app = get_object_or_404(MobileApp, slug=kwargs['app_slug'])
        app_version = get_object_or_404(AppVersion, mobile_app=app, version_number=kwargs['version_number'])
#         app_version = AppVersion.objects.filter(mobile_app=app, version_number=kwargs['version_number']).first()
        context = {'app_version': app_version, 'mobile_app': app}
        return render(request, 'management/app_version_detail.html', context)

@permission_required('polls.can_vote')    
def update_version_status(request):
    if request.is_ajax():
        app_slug = request.POST['app_slug']
        app_version_number = request.POST['version_number']
        status = request.POST['approve_status']
        app = MobileApp.objects.get(slug=app_slug)
        
        AppVersion.objects.filter(mobile_app=app, version_number=app_version_number)\
        .update(approve_status=status, approved_time=datetime.now(), approved_by=request.user)
        return JsonResponse({'status': 1}, safe=False)

@permission_required('polls.can_vote')    
def update_app_active(request):
    if request.is_ajax():
        app = get_object_or_404(MobileApp, slug=request.POST['app_slug'])
        app.is_active = True if int(request.POST['status']) == 1 else False
        app.save()
        return JsonResponse({'status': 1}, safe=False)
    
@login_required    
def upload_video(request):
    if request.is_ajax():
        video = Video()
        video.save()
        video.refresh_from_db()
        
        video_file = request.FILES['video']
        extension = video_file.name.split('.')[-1]
        base_name = 'videos/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.' + extension
        file_name = settings.MEDIA_ROOT + base_name
        with open(file_name, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        upload_file_task.delay(file_name, 'videos/', video.id, 'management_video', 'file')
        
        context = {'video_id': video.id}
        return JsonResponse(context, safe=False)
    
@login_required    
def upload_apk(request):
    if request.is_ajax():
        apk = ApkFile()
        apk.save()
        apk.refresh_from_db()
        
        apk_file = request.FILES['apk']
        extension = apk_file.name.split('.')[-1]
        base_name = 'apk/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.' + extension
        file_name = settings.MEDIA_ROOT + base_name
        with open(file_name, 'wb+') as destination:
            for chunk in apk_file.chunks():
                destination.write(chunk)
        upload_file_task.delay(file_name, 'apk/', apk.id, 'management_apkfile', 'file')
        
        context = {'apk_id': apk.id}
        return JsonResponse(context, safe=False)
        
    
class BannerListView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    def get(self, request, *args, **kwargs):
        all_banners = Banner.objects.all()
        paginator = Paginator(all_banners, 5)
        page = request.GET.get('page')
        page_banners = paginator.get_page(page)
        return render(request, 'management/banner_list.html', {'page_banners': page_banners})
    
class BannerEditView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    
    def get(self, request, *args, **kwargs):
        if 'id' in kwargs:
            banner_id = kwargs['id']
            banner = get_object_or_404(Banner, id=kwargs['id'])
            bannerForm = BannerForm(instance=banner)
        else:
            banner_id = None
            bannerForm = BannerForm()
            
        return render(request, 'management/add_banner.html', {'bannerForm': bannerForm, 'banner_id': banner_id})
    
    def post(self, request, *args, **kwargs):
        if 'id' in kwargs:
            banner = get_object_or_404(Banner, id=kwargs['id'])
        else:
            banner = Banner()    
            
        bannerForm = BannerForm(request.POST, request.FILES, instance=banner)
            
        if bannerForm.is_valid():
            bannerForm.save()
            return redirect('management:banner_list')
        return render(request, 'management/add_banner.html', {'bannerForm': bannerForm})
    
class BannerDeleteView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    
    def get(self, request, *args, **kwargs):
        banner = get_object_or_404(Banner, id=kwargs['id'])
        banner.delete()
        return redirect('management:banner_list')
    
def index(request):
    if request.user.has_perm('management.can_approve_app'):
        return redirect('management:app_table_basic')
    elif request.user.is_authenticated:
        return redirect('management:app_table_uploader')