from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View
from management.models import InspiredVideo, VideoAlbum
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
            pdf_doc = get_object_or_404(InspiredVideo, slug=slug)
            pdf_form = InspiredVideoForm(instance=pdf_doc)
            pdf_file_list = [pdf_file for pdf_file in pdf_doc.pdf_files.all()]    
            pdf_file_id_list = [str(pdf_file.id) for pdf_file in pdf_file_list]
            pdf_file_path_list = [pdf_file.file.url for pdf_file in pdf_file_list]
            pdf_file_name_list = [os.path.split(filepath)[1] for filepath in pdf_file_path_list]
            
            context = {'pdf_form': pdf_form, 
                       'slug': slug, 
                       'pdf_file_ids': ','.join(pdf_file_id_list), 
                       'pdf_file_name_list': pdf_file_name_list,
                       'pdf_file_path_list': pdf_file_path_list}
        else:
            policy, authorization = get_upyun_signature()
            initial_data = {'upload_by': request.user,
                            'policy': policy,
                            'authorization': authorization,
                            }
            slug = None
            video_form = InspiredVideoForm(initial=initial_data)
            upyun = default_storage.up
            context = {'video_form': video_form, 'slug': slug, 'upyun_url': 'http://%s/%s' % (upyun.endpoint, upyun.service)}
            
        return render(request, 'management/add_inspired_video.html', context)
    
    def post(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            slug = kwargs['slug']
            pdf_doc = get_object_or_404(InspiredVideo, slug=kwargs['slug'])
            pdf_file_list = [pdf_file for pdf_file in pdf_doc.pdf_files()]    
            pdf_file_id_list = [str(pdf_file.id) for pdf_file in pdf_file_list]
            pdf_file_path_list = [pdf_file.file.url for pdf_file in pdf_file_list]
            pdf_file_name_list = [os.path.split(filepath)[1] for filepath in pdf_file_path_list]
            
            pdfForm = InspiredVideoForm(request.POST, request.FILES, instance=pdf_doc)
            
            context = {'pdf_form': pdfForm, 
                       'slug': slug, 
                       'pdf_file_ids': ','.join(pdf_file_id_list), 
                       'pdf_file_name_list': pdf_file_name_list}
        else:
            slug = None
            initial_data = {'upload_by': request.user}
            pdf_doc = InspiredVideo()
            pdfForm = InspiredVideoForm(request.POST, request.FILES, initial=initial_data)
            
            context = {'pdf_form': pdfForm, 'slug': slug}
            
        if pdfForm.is_valid():
            pdf_doc = pdfForm.save()
            pdf_file_ids = pdfForm.cleaned_data['pdf_file_ids'].split(',')
#             pdf_file_list = [pdf_file for pdf_file in PDFFile.objects.filter(id__in=pdf_file_ids)]
#             pdf_doc.pdf_files.set(pdf_file_list)
            return redirect('management:pdf_list')
        
        
        return render(request, 'management/add_pdf.html', context)
    
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