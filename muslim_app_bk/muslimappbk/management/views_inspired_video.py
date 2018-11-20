from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View
from management.models import InspiredVideo, VideoAlbum, Video
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from management.forms import InspiredVideoForm
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.views.decorators.csrf import csrf_exempt, csrf_protect 
from django.conf import settings
from management.tasks import upload_file_task
from django.http import JsonResponse
from datetime import datetime
from django.core.files.storage import default_storage
from upyun.modules import sign
from upyun.modules.httpipe import cur_dt
import base64, time, json, logging, os, random, string
from django.db.models.fields import related

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')    
class InspiredVideoListView(View):
    def get(self, request, *args, **kwargs):
        video_list = InspiredVideo.objects.all()
        context = {'video_list': video_list}
        return render(request, 'management/inspired_video_table.html', context)
 
@method_decorator(login_required, name='dispatch')   
class InspiredVideoEditView(View):    
    def get(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            slug = kwargs['slug']
            policy, authorization = get_upyun_signature()
            initial_data = {'upload_by': request.user,
                            'policy': policy,
                            'authorization': authorization,
                            }
            inspired_video = get_object_or_404(InspiredVideo, slug=slug)
            latest_valid_video = inspired_video.latest_valid_video()
            if latest_valid_video is not None:
                initial_data['video_id'] = latest_valid_video.id
                
            video_form = InspiredVideoForm(instance=inspired_video, initial=initial_data)
            upyun = default_storage.up
            context = {'video_form': video_form, 
                       'slug': slug,
                       'upyun_url': 'http://%s/%s' % (upyun.endpoint, upyun.service)}
        else:
            policy, authorization = get_upyun_signature()
            initial_data = {'upload_by': request.user,
                            'policy': policy,
                            'authorization': authorization,
                            }
            slug = None
            video_form = InspiredVideoForm(initial=initial_data)
            upyun = default_storage.up
            context = {'video_form': video_form, 
                       'slug': slug, 
                       'upyun_url': 'http://%s/%s' % (upyun.endpoint, upyun.service)}
            
        return render(request, 'management/add_inspired_video.html', context)
    
    def post(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            slug = kwargs['slug']
            inspired_video = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
            policy, authorization = get_upyun_signature()
            initial_data = {'upload_by': request.user,
                            'policy': policy,
                            'authorization': authorization,
                            }
            latest_valid_video = inspired_video.latest_valid_video()
            if latest_valid_video is not None:
                initial_data['video_id'] = latest_valid_video.id
                
            video_form = InspiredVideoForm(request.POST, instance=inspired_video, initial=initial_data)
            upyun = default_storage.up
            context = {'video_form': video_form, 
                       'slug': slug,
                       'upyun_url': 'http://%s/%s' % (upyun.endpoint, upyun.service)}
        else:
            slug = None
            policy, authorization = get_upyun_signature()
            initial_data = {'upload_by': request.user,
                            'policy': policy,
                            'authorization': authorization,
                            }
            video_form = InspiredVideoForm(request.POST, initial=initial_data)
            upyun = default_storage.up
            context = {'video_form': video_form, 
                       'slug': slug, 
                       'upyun_url': 'http://%s/%s' % (upyun.endpoint, upyun.service)}
            
        if video_form.is_valid():
            inspired_video = video_form.save()
            video_id = video_form.cleaned_data['video_id']
            video = Video.objects.get(id=video_id)
            related_object = video.content_object
            if related_object is None:
                video.content_object = inspired_video
                video.save()
            return redirect('management:inspired_video_list')
        
        logger.info('video_for error data------------------------------------')
        logger.info(video_form.errors.as_data())
        return render(request, 'management/add_inspired_video.html', context)
    
@method_decorator(login_required, name='dispatch')     
class InspiredVideoDeleteView(View):    
    def get(self, request, *args, **kwargs):
        pdf = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
        pdf.delete()
        return redirect('management:pdf_list')
    
@method_decorator(login_required, name='dispatch')     
class InspiredVideoDetailView(View):    
    def get(self, request, *args, **kwargs):
        pdfdoc = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
        pdf_file_name_list = [os.path.split(pdf_file.file.path)[1] for pdf_file in pdfdoc.pdf_files.all()]
        context = {'pdfdoc': pdfdoc, 'pdf_file_name_list': pdf_file_name_list}
        return render(request, 'management/pdf_detail.html', context)
        
@login_required 
@csrf_exempt   
def upload_inspired_video(request):
    request.upload_handlers = [TemporaryFileUploadHandler(request)]
    return _upload_inspired_video(request)
 
@csrf_protect
def _upload_inspired_video(request):        
    if request.is_ajax():
        video_file = request.FILES.getlist('video')
                    
        file_path = video_file.temporary_file_path()
        logger.info('temporary file path:' + file_path)
        dir_name = os.path.join('pdf', ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)))
        os.mkdir(settings.MEDIA_ROOT + dir_name)
        base_name = os.path.join(dir_name, video_file.name)
        file_name = os.path.join(settings.MEDIA_ROOT, base_name)
        os.rename(file_path, file_name)
        os.chmod(file_name, 0o755)
#             upload_file_task.delay(file_name, 'pdf/', pdf_file.id, 'management_pdffile', 'file', random_folder=True)
        
#         context = {'pdf_ids': pdf_ids}
#         return JsonResponse(context, safe=False)
    
@permission_required('management.can_approve_app')    
def update_inspired_video_status(request):
    if request.is_ajax():
        pdf_slug = request.POST['pdf_slug']
        status = request.POST['approve_status']
        remark = request.POST['remark']
        pdfdoc = InspiredVideo.objects.filter(slug=pdf_slug).update(approve_status=status, 
                                                            approved_time=datetime.now(), 
                                                            approved_by=request.user, 
                                                            remark=remark)
        return JsonResponse({'status': 1}, safe=False)
    
def get_upyun_signature():
    save_key = '/%s' % default_storage._get_key_name(f'videos/{time.time()}')
    logger.info('signature save-key:' + save_key)
    upyun = default_storage.up
    now = cur_dt()
    data = {
            'bucket': upyun.service,
            'expiration': 1800 + int(time.time()),
            'save-key': save_key,
            'date': now
        }
    policy = base64.b64encode(json.dumps(data).encode()).decode()
    signature = sign.make_signature(
        username = upyun.username, 
        password = upyun.password,
        method = "POST",
        uri = '/%s' % upyun.service,
        date = now,
        policy = policy)
    return (policy, signature)