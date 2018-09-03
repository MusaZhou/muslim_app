from django.shortcuts import render, redirect
from django.conf import settings
from management.forms import AddAppModelForm, AddAppVersionModelForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from management.models import Image, MobileApp, AppVersion
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def add_mobile_app(request):
    if request.method == 'POST':
        addAppModelForm = AddAppModelForm(request.POST)
        addAppVersionModelForm = AddAppVersionModelForm(request.POST)

        if addAppModelForm.is_valid()\
        and addAppVersionModelForm.is_valid():

            newApp = addAppModelForm.save(commit=False)
            newApp.upload_by = request.user
            newApp.save()
            addAppModelForm.save_m2m()

            newAppVersion = addAppVersionModelForm.save(commit=False)
            newAppVersion.upload_by = request.user
            newAppVersion.mobile_app = newApp
            newAppVersion.full_clean()
            newAppVersion.save()

            imgIds = addAppModelForm.cleaned_data['imgIds'];
            logger.debug('imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
                for img in Image.objects.filter(id__in=imgIds):
                    img.content_object = newApp;
                    img.save()

            return HttpResponse('success')
    else:
        addAppModelForm = AddAppModelForm()
        addAppVersionModelForm = AddAppVersionModelForm()
    return render(request,
                  'management/add_mobile_app.html',
                    {'addAppModelForm': addAppModelForm,
                    'addAppVersionModelForm': addAppVersionModelForm})

class ImageFieldView(View):
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

class UpdateMobileAppView(View):
    def get(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug']);
        app_version = AppVersion.objects.filter(mobile_app=mobile_app).latest('-approved_time')
        updateAppVersionModelForm = AddAppVersionModelForm(instance=app_version)
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
                                                                     'updateAppVersionModelForm': updateAppVersionModelForm,
                                                                     'imgUrls': imgUrls})

    def post(self, request, *args, **kwargs):
        mobile_app = MobileApp.objects.get(slug=kwargs['slug'])
        logger.debug('mobiel app description:' + mobile_app.description)
        appImages = mobile_app.images.all()
        imgIds = []
        for img in appImages:
            imgIds.append(str(img.id))
        imgIds = ','.join(imgIds)
        updateAppModelForm = AddAppModelForm(request.POST, instance=mobile_app, initial={'imgIds': imgIds})

        if updateAppModelForm.is_valid():
            logger.debug('before form save')
            updateAppModelForm.save()
            logger.debug('after form save')
            working_o = updateAppModelForm.instance
            logger.debug('instance id:' + str(working_o.id))
            logger.debug('instance name:' + working_o.name)
            logger.debug('instance description:' + working_o.description)
            logger.debug('instance category:' + str(working_o.category))
            logger.debug('instance upload_by:' + str(working_o.upload_by))
            logger.debug('instance upload_date:' + str(working_o.upload_date))
            logger.debug('instance slug:' + working_o.slug)

            logger.debug('before instance save')
            working_o.save()
            logger.debug('after instance save')
            logger.debug('before test save')
            test_app = MobileApp.objects.get(id=9)
            test_app.description = 'af11111'
            test_app.save()
            logger.debug('after test save')

            logger.debug('form is bound:'+str(updateAppModelForm.is_bound))
            logger.debug('form has changed:'+str(updateAppModelForm.has_changed()))
            logger.debug('changed data:'+' '.join(updateAppModelForm.changed_data))
            logger.debug('field description(cleaned):'+updateAppModelForm.cleaned_data['description'])
            logger.debug('field category(cleaned):'+ str(updateAppModelForm.cleaned_data['category']))
            logger.debug('field video_url(cleaned):'+updateAppModelForm.cleaned_data['video_url'])

            # updateAppModelForm.instance.save()

            imgIds = updateAppModelForm.cleaned_data['imgIds']
            logger.debug('new imgIds:' + imgIds)
            if imgIds:
                imgIds = imgIds.split(',')
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

            return HttpResponse('ok')

        return redirect('management:update_mobile_app', slug=kwargs['slug'])
