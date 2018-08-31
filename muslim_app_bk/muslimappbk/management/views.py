from django.shortcuts import render, redirect
from django.conf import settings
from management.forms import AddAppModelForm, AddAppVersionModelForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from management.models import Image
from django.http import HttpResponse

# Create your views here.
def addMobileApp(request):
    ImageInlineFormset = generic_inlineformset_factory(Image, fields=('picture',))
    if request.method == 'POST':
        addAppModelForm = AddAppModelForm(request.POST)
        addAppVertionModelForm = AddAppModelForm(request.POST)
        imageInlineFormset = ImageInlineFormset(request.POST, request.FILES)

        if addAppModelForm.is_valid()
            and addAppVersionModelForm.is_valid()
            and imageInlineFormset.is_valid():

            newApp = addAppModelForm.save(commit=False)
            newApp.upload_by = request.user
            newApp.save()
            addAppModelForm.save_m2m()

            newAppVersion = addAppVersionModelForm.save(commit=False)
            newAppVersion.upload_by = request.user
            newAppVersion.mobile_app = newApp
            newAppVersion.save()

            images = imageInlineFormset.save(commit=False)
            for image in images:
                image.content_object = newApp
                image.save()

            return HttpResponse('success')
    else
        imageInlineFormset = ImageInlineFormset()
        return render(request, 'add_app.html', {'addAppModelForm': addAppModelForm,
                                                'addAppVertionModelForm': addAppVertionModelForm,
                                                'imageInlineFormset': imageInlineFormset})
