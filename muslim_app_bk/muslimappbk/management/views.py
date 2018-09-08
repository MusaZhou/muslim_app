from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from management.forms import AddAppModelForm, AddAppVersionModelForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from management.models import Image, MobileApp, AppVersion
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.core.paginator import Paginator, Page
from django.core.exceptions import ValidationError
from datetime import date
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin

logger = logging.getLogger(__name__)
                
# Create your views here.
@login_required
def add_mobile_app(request):
    if request.method == 'POST':
        addAppModelForm = AddAppModelForm(request.POST)
        addAppVersionModelForm = AddAppVersionModelForm(request.POST, request.FILES)

        if addAppModelForm.is_valid()\
        and addAppVersionModelForm.is_valid():

            newApp = addAppModelForm.save(commit=False)
            newApp.upload_by = request.user
            newApp.save()
            addAppModelForm.save_m2m()

            newAppVersion = addAppVersionModelForm.save(commit=False)
            newAppVersion.mobile_app = newApp
            try:
                newAppVersion.full_clean()
                newAppVersion.save()
    
                imgIds = addAppModelForm.cleaned_data['imgIds'];
                logger.debug('imgIds:' + imgIds)
                if imgIds:
                    imgIds = imgIds.split(',')
                    for img in Image.objects.filter(id__in=imgIds):
                        img.content_object = newApp;
                        img.save()
    
                return redirect('management:app_table_basic')
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
        updateAppModelForm = AddAppModelForm(instance=mobile_app, initial={'imgIds': imgIds})
        return render(request, 'management/update_mobile_app.html', {'updateAppModelForm': updateAppModelForm,
                                                                     'imgUrls': imgUrls})

    def post(self, request, *args, **kwargs):
        mobile_app = get_object_or_404(MobileApp, slug=kwargs['slug'])
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app)
        imgUrls = []
        
        if updateAppModelForm.is_valid():
            mobile_app = updateAppModelForm.save()
            imgIds = updateAppModelForm.cleaned_data['imgIds']
            logger.debug('new imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
                update_app_images(imgIds, mobile_app)

            return redirect('management:app_table_basic')
        else:
            appImages = mobile_app.images.all()
            imgUrls = []
            for img in appImages:
                imgUrls.append(img.picture.url)
                
        return render(request, 'management/update_mobile_app.html', 
                          {'updateAppModelForm': updateAppModelForm,
                             'imgUrls': imgUrls})
            
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
            new_app_version = addAppVersionModelForm.save(commit=False)
            new_app_version.upload_by = request.user
            new_app_version.mobile_app = mobile_app
            try:
                new_app_version.full_clean()
                mobile_app = updateAppModelForm.save()
                new_app_version.save()
                imgIds = updateAppModelForm.cleaned_data['imgIds']
                if imgIds:
                    imgIds = imgIds.split(',')
                    update_app_images(imgIds, mobile_app)
                
                return redirect('management:app_table_basic')
        
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