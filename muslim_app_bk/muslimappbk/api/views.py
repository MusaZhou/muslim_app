
from management.models import MobileApp, InspiredVideo, Video, Image
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
from django.urls.conf import path
from management.tasks import update_video_path_task

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

@csrf_exempt
def process_video_notify(request):
    logger.info('process video notify:')
    logger.info(request.POST.dict)
    if request.POST['status_code'] == '200':
        logger.info('status ok')
        path = request.POST['path[0]'].split(settings.MEDIA_URL)[1]
        task_id = request.POST['task_id']
        logger.info('path:' + path)
        logger.info('task_id:' + task_id)
        video_info = json.loads(base64.b64decode(request.POST['info']))
        logger.info(video_info)
        width = video_info['streams'][0]['video_width']
        height = video_info['streams'][0]['video_height']
        duration = video_info['streams'][0]['duration']
        logger.info('video width:' + str(width))
        logger.info('video height:' + str(height))
        logger.info('duration:' + str(int(duration)))
        update_video_path_task.apply_async(kwargs={ 'path': path, 'task_id': task_id, 'width': width, 'height': height, 'duration': duration}, count_down=3)
    return HttpResponse('thanks')

def notify_video_process_task(request):
    task_id = request.POST['task_id']
    video = Video.objects.create(upyun_task_id=task_id)
    return JsonResponse({'video_id': video.id})

def _image_tasks(request, save_key):
    return [{
            "name": "thumb",
            "x-gmkerl-thumb": "videoalbum",
            "save_as": save_key.replace('original', 'thumbnail', 1),
            "notify_url": request.build_absolute_uri(reverse('api:image_thumbnail_notify'))
        }]
    
# @csrf_exempt
def get_image_upload_signature(request):
    file_name, ext = os.path.splitext(request.POST['file_name'])
    
    if ext:
        name = f"pictures/album/original/{file_name}_{time.time()}{ext}"
    else:
        name = f"pictures/album/original/{file_name}_{time.time()}"
    save_key = '/%s' % default_storage._get_key_name(name)
    logger.info('signature save-key:' + save_key)
    upyun = default_storage.up
    now = cur_dt()
    image_tasks = _image_tasks(request, save_key)
    data = {
            'bucket': upyun.service,
            'expiration': 1800 + int(time.time()),
            'save-key': save_key,
            'date': now,
            'apps': image_tasks
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

def notify_image_process_task(request):
    task_id = request.POST['task_id']
    image = Image.objects.create(upyun_task_id=task_id)
    return JsonResponse({'image_id': image.id})

@csrf_exempt
def image_thumbnail_notify(request):
    logger.info('process video notify:')
    logger.info(request.POST.dict)
    if request.POST['status_code'] == '200':
        logger.info('status ok')
        path = request.POST['path[0]'].split(settings.MEDIA_URL)[1]
        task_id = request.POST['task_id']
        logger.info('path:' + path)
        logger.info('task_id:' + task_id)
        video_info = json.loads(base64.b64decode(request.POST['info']))
        logger.info(video_info)
        width = video_info['streams'][0]['video_width']
        height = video_info['streams'][0]['video_height']
        duration = video_info['streams'][0]['duration']
        logger.info('video width:' + str(width))
        logger.info('video height:' + str(height))
        logger.info('duration:' + str(int(duration)))
        update_video_path_task.apply_async(kwargs={ 'path': path, 'task_id': task_id, 'width': width, 'height': height, 'duration': duration}, count_down=3)
    return HttpResponse('thanks')