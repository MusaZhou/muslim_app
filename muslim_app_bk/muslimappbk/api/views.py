
from management.models import MobileApp, InspiredVideo, Video, Image
from api.serializers import AppSerializer, InspiredVideoSerializer
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
from management.tasks import update_video_path_task, update_image_path_task, update_video_thumbnail_task
from email.policy import HTTP

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
    video_process = _video_process(request, file_name)
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

def _video_process(request, file_name):
    thumbnail_name = f"pictures/video_thumbnail/{file_name}_{time.time()}.jpg"
    thumbnail_save_as = '/%s' % default_storage._get_key_name(thumbnail_name)
    
    return [{
            "name": "naga",
            "type": "video",
            "avopts": "/f/mp4",
            "return_info": True,
            "notify_url": request.build_absolute_uri(reverse('api:process_video_notify'))
#             "notify_url": 'https://uptool.tingfun.net/echo.php'
        },
        {
            "name": "naga",
            "type": "thumbnail",
            "avopts": "/o/true/n/1",
            "return_info": True,
            "save_as": thumbnail_save_as,
            "notify_url": request.build_absolute_uri(reverse('api:process_video_thumbnail_notify'))
#             "notify_url": 'https://uptool.tingfun.net/echo.php'
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

@csrf_exempt
def process_video_thumbnail_notify(request):
    logger.info('process_video_thumbnail_notify:')
    logger.info(request.POST.dict)
    if request.POST['status_code'] == '200':
        logger.info('status ok')
        path = request.POST['path[0]'].split(settings.MEDIA_URL)[1]
        task_id = request.POST['task_id']
        logger.info('path:' + path)
        logger.info('task_id:' + task_id)
        update_video_thumbnail_task.apply_async(kwargs={ 'picture_path': path, 'task_id': task_id}, count_down=3)
    return HttpResponse('thanks')

@csrf_exempt
def notify_video_process_task(request):
    task_ids = json.loads(request.POST['task_ids'])
    logger.info(task_ids)
    video = Video.objects.create(upyun_task_id=task_ids[0])
    image = Image.objects.create(upyun_task_id=task_ids[1])
    return JsonResponse({'video_id': video.id, 'image_id': image.id})

def _image_tasks(request, save_key, thumbnail_pattern):
    return [{
            "name": "thumb",
            "x-gmkerl-thumb": thumbnail_pattern,
            "save_as": save_key.replace('original', 'thumbnail', 1),
            "notify_url": request.build_absolute_uri(reverse('api:image_thumbnail_notify'))
#             "notify_url": 'https://uptool.tingfun.net/echo.php'
        }]
    
# @csrf_exempt
# folder_name: such folder name will be composed into picutre/{folder_name}/original/....
def get_image_upload_signature(request):
    file_name, ext = os.path.splitext(request.POST['file_name'])
    folder_name = request.POST['folder_name']
    thumbnail_pattern = request.POST['thumbnail_pattern']
    
    if ext:
        name = f"pictures/{folder_name}/original/{file_name}_{time.time()}{ext}"
    else:
        name = f"pictures/{folder_name}/original/{file_name}_{time.time()}"
    save_key = '/%s' % default_storage._get_key_name(name)
    logger.info('signature save-key:' + save_key)
    upyun = default_storage.up
    now = cur_dt()
    image_tasks = _image_tasks(request, save_key, thumbnail_pattern)
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
    original_path = request.POST['original_path'].replace(settings.MEDIA_URL, '', 1)
    image = Image.objects.create(upyun_task_id=task_id, picture=original_path)
    return JsonResponse({'image_id': image.id})

@csrf_exempt
def image_thumbnail_notify(request):
    logger.info('process image notify:')
#     logger.info(request.body)
    logger.info(request.body.decode())
    data = json.loads(request.body.decode())
    if data['status_code'] == 200:
        logger.info('status ok')
        path = data['imginfo']['path'].split(settings.MEDIA_URL)[1]
        task_id = data['task_id']
        logger.info('path:' + path)
        logger.info('task_id:' + task_id)
        width = data['imginfo']['width']
        height = data['imginfo']['height']
        logger.info('image width:' + str(width))
        logger.info('image height:' + str(height))
        update_image_path_task.apply_async(kwargs={ 'thumbnail_path': path, 'task_id': task_id, 'width': width, 'height': height}, count_down=3)
    return HttpResponse('thanks')

class InspiredVideoListView(generics.ListAPIView):
    serializer_class = InspiredVideoSerializer
    
    def get_queryset(self):
        page = int(self.request.query_params.get('page', 1))
        tags = json.loads(self.request.query_params.get('tags', "[]"))
        album = int(self.request.query_params.get('album', 0))
        logger.info('page: ' + str(page))
        logger.info('tags id:' + str(tags))
        logger.info('album id' + str(album));
        if tags != []:
            video_list_all = InspiredVideo.shown_videos.filter(tags__id__in=tags).distinct()
        elif album != 0:
            video_list_all = InspiredVideo.shown_videos.filter(album_id=album)
        else:
            video_list_all = InspiredVideo.shown_videos.all()
            
        paginator = Paginator(video_list_all, 12)
        try:
            video_list = paginator.page(page)
            return video_list.object_list
        except InvalidPage:
            return InspiredVideo.objects.none()
        
# @csrf_exempt
def get_file_upload_signature(request):
    file_name, ext = os.path.splitext(request.POST['file_name'])
    folder_name = request.POST['folder_name']
    big = int(request.POST['big'])
    
    if ext:
        name = f"{folder_name}/{file_name}_{time.time()}{ext}"
    else:
        name = f"{folder_name}/{file_name}_{time.time()}"
    save_key = '/%s' % default_storage._get_key_name(name)
    logger.info('signature save-key:' + save_key)
    upyun = default_storage.up
    now = cur_dt()
    data = {
            'bucket': upyun.service,
            'expiration': 1800 + int(time.time()),
            'save-key': save_key,
            'date': now,
        }
    
    if big:
        file_size = request.POST['file_size']
        data['content-length'] = file_size
        
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
