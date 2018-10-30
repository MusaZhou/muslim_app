from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from management.models import PDFDoc, PDFFile
from django.core.paginator import Paginator, Page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from management.forms import PDFDocModelForm
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import logging, os, random, string
from django.conf import settings
from management.tasks import upload_file_task
from django.http import JsonResponse

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
            pdf = get_object_or_404(PDFDoc, slug=slug)
            pdf_form = PDFDocModelForm(instance=pdf)
        else:
            slug = None
            pdf_form = PDFDocModelForm()
        
        context = {'pdfForm': pdf_form, 'slug': slug}
        return render(request, 'management/add_pdf.html', context)
    
    def post(self, request, *args, **kwargs):
        if 'slug' in kwargs:
            pdf = get_object_or_404(PDFDoc, id=kwargs['slug'])
        else:
            pdf = PDFDoc()    
            
        pdfForm = PDFDocModelForm(request.POST, request.FILES, instance=pdf)
            
        if pdfForm.is_valid():
            pdfForm.save()
            return redirect('management:pdf_list')
        return render(request, 'management/add_pdf.html', {'pdfForm': pdfForm})
    
@method_decorator(login_required, name='dispatch')     
class PDFDeleteView(View):    
    def get(self, request, *args, **kwargs):
        pdf = get_object_or_404(PDFDoc, id=kwargs['slug'])
        pdf.delete()
        return redirect('management:pdf_list')
    
@method_decorator(login_required, name='dispatch')     
class PDFDetailView(View):    
    def get(self, request, *args, **kwargs):
        pdf = get_object_or_404(PDFDoc, id=kwargs['slug'])
        context = {'pdf': pdf}
        return redirect('management:pdf_detail', context)

@login_required 
@csrf_exempt   
def upload_pdf(request):
    request.upload_handlers = [TemporaryFileUploadHandler(request)]
    return _upload_pdf(request)
 
@csrf_protect
def _upload_pdf(request):        
    if request.is_ajax():
        pdf = PDFFile()
        pdf.save()
        pdf.refresh_from_db()
        
        pdf_file = request.FILES['pdf']
        file_path = pdf_file.temporary_file_path()
        logger.info('temporary file path:' + file_path)
        base_name = 'pdf/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.pdf'
        file_name = settings.MEDIA_ROOT + base_name
        os.rename(file_path, file_name)
        os.chmod(file_name, 0o755)
        upload_file_task.delay(file_name, 'pdf/', pdf.id, 'management_pdffile', 'file')
        
        context = {'pdf_id': pdf.id}
        return JsonResponse(context, safe=False)