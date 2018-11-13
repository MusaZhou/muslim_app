
from management.models import MobileApp
from api.serializers import AppSerializer
from rest_framework import generics
from django.db.models import F
from django.http import HttpResponse, JsonResponse
import upyun
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import http_date
import hashlib
from django.core.paginator import InvalidPage, Paginator

class AppListView(generics.ListAPIView):
    serializer_class = AppSerializer
    
    def get_queryset(self):
        category_id = int(self.request.query_params.get('cate_id', 9999))
        page = int(self.request.query_params.get('page', 1))
        
        if category_id == 9999:
            mobile_list_all = MobileApp.shown_apps.all()
        else:    
            mobile_list_all = MobileApp.shown_apps.filter(category__id=category_id)
            
        paginator = Paginator(mobile_list_all, 9)
        try:
            mobile_list = paginator.page(page)
            return mobile_list.object_list
        except InvalidPage:
            return MobileApp.objects.none()
    
def app_download_count(request):
    app_slug = request.GET['app_slug']
    MobileApp.objects.filter(slug=app_slug).update(download_count=F('download_count')+1)
    return HttpResponse(status=200)


def get_video_upload_signature(request):
    file_name = request.POST['file_name']
    pass