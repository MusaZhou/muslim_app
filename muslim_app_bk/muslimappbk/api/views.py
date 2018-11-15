
from management.models import MobileApp
from api.serializers import AppSerializer
from rest_framework import generics
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import InvalidPage, Paginator
from django.core.files.storage import default_storage
from upyun.modules import sign
from upyun.modules.httpipe import cur_dt
import base64, time, json, logging, os, random, string
from django.urls import reverse

logger = logging.getLogger(__name__)

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

# @csrf_exempt
def get_video_upload_signature(request):
    file_name, ext = os.path.splitext(request.POST['file_name'])
    file_size = request.POST['file_size']
    
    if ext:
        name = f"videos/{file_name}_{time.time()}{ext}"
    else:
        name = f"videos/{file_name}_{time.time()}"
    save_key = '/%s' % default_storage._get_key_name(name)
    logger.info('signature save-key:' + save_key)
    upyun = default_storage.up
    now = cur_dt()
    video_process = _video_process(request)
    data = {
            'bucket': upyun.service,
            'expiration': 1800 + int(time.time()),
            'content-length': file_size,
            'save-key': save_key,
            'date': now,
            'apps': video_process
        }
    policy = base64.b64encode(json.dumps(data).encode()).decode()
    authorization = sign.make_signature(
        username = upyun.username, 
        password = upyun.password,
        method = "POST",
        uri = '/%s' % upyun.service,
        date = now,
        policy = policy)
    data = {'policy': policy, 'authorization': authorization}
    return JsonResponse(data)

def _video_process(request):
    return [{
            "name": "naga",
            "type": "video",
            "avopts": "/f/mp4",
            "return_info": True,
            "notify_url": request.build_absolute_uri(reverse('api:process_video_notify'))
        }]

def process_video_notify(request):
    logger.info('process video notify:')
    logger.info(request)