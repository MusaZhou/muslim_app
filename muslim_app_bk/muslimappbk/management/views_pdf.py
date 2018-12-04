from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View
from management.models import PDFDoc, PDFFile
from django.core.paginator import Paginator, Page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from management.forms import PDFDocForm
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import logging, os, random, string
from django.conf import settings
from management.tasks import upload_file_task
from django.http import JsonResponse
from datetime import datetime

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')    
class PDFListView(View):
    def get(self, request, *args, **kwargs):
        pdf_list = PDFDoc.objects.all()
        context = {'pdf_list': pdf_list}
        return render(request, 'management/pdf_table.html', context)
 
@method_decorator(login_required, name='dispatch')   
class PDFEditView(View):    
    def get(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            slug = kwargs['slug']
            pdf_doc = get_object_or_404(PDFDoc, slug=slug)
            
            pdf_file_list = [pdf_file for pdf_file in pdf_doc.pdf_files.all()]    
            pdf_file_path_list = [pdf_file.file.url for pdf_file in pdf_file_list]
            pdf_file_name_list = [os.path.split(filepath)[1] for filepath in pdf_file_path_list]
            pdf_file_urls = ','.join(pdf_file_path_list)
            initial_data = {'pdf_file_urls': pdf_file_urls}
            pdf_form = PDFDocForm(instance=pdf_doc, initial=initial_data)
            
            context = {'pdf_form': pdf_form, 
                       'slug': slug, 
                       'pdf_file_name_list': pdf_file_name_list,
                       'pdf_file_path_list': pdf_file_path_list}
        else:
            initial_data = {'upload_by': request.user}
            slug = None
            pdf_form = PDFDocForm(initial=initial_data)
        
            context = {'pdf_form': pdf_form, 'slug': slug}
            
        return render(request, 'management/add_pdf.html', context)
    
    def post(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            slug = kwargs['slug']
            pdf_doc = get_object_or_404(PDFDoc, slug=kwargs['slug'])
            pdf_file_list = [pdf_file for pdf_file in pdf_doc.pdf_files.all()]    
            pdf_file_path_list = [pdf_file.file.url for pdf_file in pdf_file_list]
            pdf_file_name_list = [os.path.split(filepath)[1] for filepath in pdf_file_path_list]
            pdf_file_urls = ','.join(pdf_file_path_list)
            initial_data = {'pdf_file_urls': pdf_file_urls}
            
            pdfForm = PDFDocForm(request.POST, instance=pdf_doc, initial=initial_data)
            
            context = {'pdf_form': pdfForm, 
                       'slug': slug, 
                       'pdf_file_name_list': pdf_file_name_list,
                       'pdf_file_path_list': pdf_file_path_list}
        else:
            slug = None
            initial_data = {'upload_by': request.user}
            pdf_doc = PDFDoc()
            pdfForm = PDFDocForm(request.POST, initial=initial_data)
            
            context = {'pdf_form': pdfForm, 'slug': slug}
            
        if pdfForm.is_valid():
            pdf_doc = pdfForm.save()
            pdf_file_urls = pdfForm.cleaned_data['pdf_file_urls'].split(',')
            
            old_pdf_files = pdf_doc.pdf_files.all()
            old_pdf_files.exclude(file__in=pdf_file_urls).delete()
            old_urls = old_pdf_files.values_list('file', flat=True)
            [PDFFile.objects.create(file=new_url, pdf_doc=pdf_doc) for new_url in pdf_file_urls if new_url not in old_urls]
            
            return redirect('management:pdf_list')
        
        return render(request, 'management/add_pdf.html', context)
    
@method_decorator(login_required, name='dispatch')     
class PDFDeleteView(View):    
    def get(self, request, *args, **kwargs):
        pdf = get_object_or_404(PDFDoc, slug=kwargs['slug'])
        pdf.delete()
        return redirect('management:pdf_list')
    
@method_decorator(login_required, name='dispatch')     
class PDFDetailView(View):    
    def get(self, request, *args, **kwargs):
        pdfdoc = get_object_or_404(PDFDoc, slug=kwargs['slug'])
        pdf_file_name_list = [os.path.split(pdf_file.file.path)[1] for pdf_file in pdfdoc.pdf_files.all()]
        context = {'pdfdoc': pdfdoc, 'pdf_file_name_list': pdf_file_name_list}
        return render(request, 'management/pdf_detail.html', context)
        
# @login_required 
# @csrf_exempt   
# def upload_pdf(request):
#     request.upload_handlers = [TemporaryFileUploadHandler(request)]
#     return _upload_pdf(request)
 
# @csrf_protect
# def _upload_pdf(request):        
#     if request.is_ajax():
#         pdf_list = request.FILES.getlist('pdf_files')
#         pdf_ids = []
#         
#         for pdf in pdf_list:
#             pdf_file = PDFFile()
#             pdf_file.save()
#             pdf_ids.append(pdf_file.id)
#             
#             file_path = pdf.temporary_file_path()
#             logger.info('temporary file path:' + file_path)
#             dir_name = os.path.join('pdf', ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)))
#             os.mkdir(settings.MEDIA_ROOT + dir_name)
#             base_name = os.path.join(dir_name, pdf.name)
#             file_name = os.path.join(settings.MEDIA_ROOT, base_name)
#             os.rename(file_path, file_name)
#             os.chmod(file_name, 0o755)
#             upload_file_task.delay(file_name, 'pdf/', pdf_file.id, 'management_pdffile', 'file', random_folder=True)
#         
#         context = {'pdf_ids': pdf_ids}
#         return JsonResponse(context, safe=False)
    
@permission_required('management.can_approve_app')    
def update_pdf_status(request):
    if request.is_ajax():
        pdf_slug = request.POST['pdf_slug']
        status = request.POST['approve_status']
        remark = request.POST['remark']
        pdfdoc = PDFDoc.objects.filter(slug=pdf_slug).update(approve_status=status, 
                                                            approved_time=datetime.now(), 
                                                            approved_by=request.user, 
                                                            remark=remark)
        return JsonResponse({'status': 1}, safe=False)