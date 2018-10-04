from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from management.models import Image, MobileApp, AppVersion
from django.core.paginator import Paginator, Page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin

@method_decorator(login_required, name='dispatch')             
class AppTableUploaderView(View):
    def get(self, request, *args, **kwargs):
        app_list = MobileApp.objects.filter(upload_by=request.user)
        paginator = Paginator(app_list, 5)
        page = request.GET.get('page')
        page_apps = paginator.get_page(page)
        
        return render(request, 'management/uploader/app_table_uploader.html', {'page_apps': page_apps})

@method_decorator(login_required, name='dispatch')    
class AppHistoryUploaderView(View):
    def get(self, request, *args, **kwargs):
        mobile_app = get_object_or_404(MobileApp, slug=kwargs['slug'])
        app_version_list = mobile_app.versions.all()
        context = {'mobile_app': mobile_app, 'app_version_list': app_version_list}
        return render(request, 'management/uploader/app_history_uploader.html', context)
    
    def post(self, request, *args, **kwargs):
        pass