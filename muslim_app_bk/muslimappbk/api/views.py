
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

class AppListView(generics.ListAPIView):
    serializer_class = AppSerializer
    
    def get_queryset(self):
        category_id = int(self.request.query_params.get('cate_id', 9999))
        if category_id == 9999:
            return MobileApp.shown_apps.all()
        return MobileApp.shown_apps.filter(category__id=category_id)
    
def app_download_count(request):
    app_slug = request.GET['app_slug']
    MobileApp.objects.filter(slug=app_slug).update(download_count=F('download_count')+1)
    return HttpResponse(status=200)

@csrf_exempt
def upyun_sign_head(request):
    date = http_date()
    data = {
            'username': settings.UPY_USERNAME,
            'password': hashlib.md5(settings.UPY_PASSWORD.encode()).hexdigest(),
            'method': request.GET['method'],
            'uri': request.GET['uri'],
            'date': date,
        }
    
    header = {'Authorization': upyun.make_signature(**data), 'X-Date': date}
    
    return JsonResponse(header, safe=False)
