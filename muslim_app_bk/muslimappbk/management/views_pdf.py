from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from management.models import PDFDoc
from django.core.paginator import Paginator, Page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from management.forms import PDFDocModelForm

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
            bannerForm = PDFDocModelForm()
            
        return render(request, 'management/add_pdf.html', {'pdfForm': pdf_form, 'slug': slug})
    
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