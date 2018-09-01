from django.shortcuts import render, redirect
from django.conf import settings
from management.forms import AddAppModelForm, AddAppVersionModelForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from management.models import Image
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from datetime import date

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
            newAppVersion.save()

            return HttpResponse('success')
    else:
        addAppModelForm = AddAppModelForm()
        addAppVersionModelForm = AddAppVersionModelForm()
        return render(request,
                      'management/add_mobile_app.html',
                        {'addAppModelForm': addAppModelForm,
                        'addAppVersionModelForm': addAppVersionModelForm})

class ImageFieldView(View):
    def post(seft, request):
        if request.is_ajax():
            files = request.FILES.getlist('images');
            print('file count:'+ ',' + str(len(files)))
            imageIds = []
            for file in files:
                image = Image(picture=file)
                image.save()
                imageIds.append(image.id)
            return JsonResponse(imageIds, safe=False)
