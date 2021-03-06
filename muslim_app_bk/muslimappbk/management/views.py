from django.shortcuts import render, redirect, get_object_or_404
from management.forms import AddAppModelForm, AddAppVersionModelForm, BannerForm
from management.models import Image, MobileApp, AppVersion, Banner, Video,\
    ApkFile
from django.http import JsonResponse
from django.views.generic import View
from django.core.paginator import Paginator, Page
from datetime import datetime
import logging, os, random, string
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin

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
            newAppVersion.save()
            
            apk_url = addAppVersionModelForm.cleaned_data['apk_url']
            ApkFile.objects.create(file=apk_url, app_version=newAppVersion)

            imgIds = addAppModelForm.cleaned_data['imgIds']
            logger.debug('imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
                for img in Image.objects.filter(id__in=imgIds):
                    img.content_object = newApp
                    img.save()
            
            video_url = addAppModelForm.cleaned_data['video_url']
            if video_url:
                video = Video(file=video_url, content_object=newApp)
                video.save()
                
            return redirect('management:app_table_basic')\
                 if user.has_perm('management.can_approve_app')\
                 else redirect('management:app_table_uploader')
    else:
        addAppModelForm = AddAppModelForm()
        addAppVersionModelForm = AddAppVersionModelForm()
        
    logger.debug('app form errors:' + ','.join(addAppModelForm.errors))
    logger.debug('app version form errors:' + ','.join(addAppVersionModelForm.errors))  
    return render(request,
                  'management/add_mobile_app.html',
                    {'addAppModelForm': addAppModelForm,
                    'addAppVersionModelForm': addAppVersionModelForm,
                    })

class UpdateMobileAppView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug']);
        appImages = mobile_app.images.all()
        imgIds = []
        imgUrls = []
        for img in appImages:
            imgIds.append(str(img.id))
            imgUrls.append(img.picture.url)
        imgIds = ','.join(imgIds)
        
        video_url = None
        last_video = mobile_app.videos.last()
        if last_video:
            video_url = last_video.file.url
        
        initial_data = {'imgIds': imgIds, 'video_url': video_url }
        updateAppModelForm = AddAppModelForm(instance=mobile_app, initial=initial_data)
        return render(request, 'management/update_mobile_app.html', {'updateAppModelForm': updateAppModelForm,
                                                                     'imgUrls': imgUrls,
                                                                     })

    def post(self, request, *args, **kwargs):
        mobile_app = get_object_or_404(MobileApp, slug=kwargs['slug'])
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app)
        imgUrls = []
        video_url = None
        
        if updateAppModelForm.is_valid():
            mobile_app = updateAppModelForm.save()
            imgIds = updateAppModelForm.cleaned_data['imgIds']
            logger.debug('new imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
                update_app_images(imgIds, mobile_app)
                
            video_url = updateAppModelForm.cleaned_data['video_url']
            
            if video_url:
                video = mobile_app.videos.last()
                if video is None:
                    video = Video(file=video_url, content_object=mobile_app)
                    video.save()
                else:
                    video.file = video_url
                    video.save()
            
            return redirect('management:index')
        else:
            appImages = mobile_app.images.all()
            imgUrls = []
            for img in appImages:
                imgUrls.append(img.picture.url)
            
            last_video = mobile_app.videos.last()
            if last_video:
                video_url = last_video.file.url
                
            if(updateAppModelForm.errors):
                    logger.info('form errors: %s', updateAppModelForm.errors.as_data())
                
        return render(request, 'management/update_mobile_app.html', 
                          {'updateAppModelForm': updateAppModelForm,
                             'imgUrls': imgUrls,
                             'video_url': video_url,
                             })
            
class AppTableBasicView(PermissionRequiredMixin, View):
    permission_required = 'management.can_approve_app'
    
    def get(self, request, *args, **kwargs):
        all_apps = MobileApp.upload_order.all()
        paginator = Paginator(all_apps, 5)
        page = request.GET.get('page')
        page_apps = paginator.get_page(page)
        
        return render(request, 'management/app_table_basic.html', {'page_apps': page_apps})

@method_decorator(login_required, name='dispatch')
class AddAppVersionView(View):
    def get(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug'])
        addAppVersionModelForm = AddAppVersionModelForm(initial={'mobile_app': mobile_app})
        appImages = mobile_app.images.all()
        imgIds = []
        imgUrls = []
        for img in appImages:
            imgIds.append(str(img.id))
            imgUrls.append(img.picture.url)
        imgIds = ','.join(imgIds)
        
        initial_data = {'imgIds': imgIds}
        updateAppModelForm = AddAppModelForm(instance=mobile_app, initial=initial_data)
        return render(request,
                  'management/add_app_version.html',
                    {'addAppVersionModelForm': addAppVersionModelForm,
                     'updateAppModelForm': updateAppModelForm,
                     'imgUrls': imgUrls})
        
    def post(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug'])
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app)
        addAppVersionModelForm = AddAppVersionModelForm(request.POST, request.FILES, initial={'mobile_app': mobile_app})
        
        if updateAppModelForm.is_valid() and addAppVersionModelForm.is_valid():
            user = request.user
            new_app_version = addAppVersionModelForm.save(commit=False)
            new_app_version.upload_by = user
            new_app_version.mobile_app = mobile_app
            mobile_app = updateAppModelForm.save()
            new_app_version.save()
            imgIds = updateAppModelForm.cleaned_data['imgIds']
            
            apk_url = addAppVersionModelForm.cleaned_data['apk_url']
            ApkFile.objects.create(file=apk_url, app_version=new_app_version)
            
            if imgIds:
                imgIds = imgIds.split(',')
                update_app_images(imgIds, mobile_app)
                
            return redirect('management:app_history', slug=mobile_app.slug)\
                 if user.has_perm('management.can_approve_app')\
                 else redirect('management:app_history_uploader', slug=mobile_app.slug)
        
            
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
        app_version_list = mobile_app.versions.all()
        context = {'mobile_app': mobile_app, 'app_version_list': app_version_list}
        return render(request, 'management/app_history.html', context)

def update_app_images(imgIds, mobile_app):
    logger.debug('new imgIds:' + ','.join(imgIds))
    if imgIds:
        new_qs = Image.objects.filter(id__in=imgIds)
        old_qs = mobile_app.images.all()
        old_qs.exclude(id__in=imgIds).delete()

        for img in new_qs:
            if not img.content_object:
                img.content_object = mobile_app;
                img.save()

                
class VersionDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        app = get_object_or_404(MobileApp.objects.prefetch_related('images', 'videos', 'tags'), slug=kwargs['app_slug'])
        app_version = get_object_or_404(AppVersion.objects.select_related('apk'), mobile_app=app, version_number=kwargs['version_number'])
        context = {'app_version': app_version, 'mobile_app': app}
        return render(request, 'management/app_version_detail.html', context)
    
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
    
def index(request):
    if request.user.has_perm('management.can_approve_app'):
        return redirect('management:app_table_basic')
    elif request.user.is_authenticated:
        return redirect('management:app_table_uploader')