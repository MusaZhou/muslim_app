from rest_framework import viewsets, status
from management.models import PDFDoc
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .permissions import ApproveAppPermission
from datetime import datetime
from rest_framework.decorators import action

class DocViewSet(viewsets.ModelViewSet):
    queryset = PDFDoc.objects.all()   
    lookup_field = 'slug'
    
    def destroy(self, request, slug=None):
        pdf = self.get_object()
        pdf.delete()
        return Response(status=status.HTTP_200_OK)
    
    def get_permissions(self):
        permission_classes = []
        if self.action == 'destroy':
            permission_classes.append(IsAuthenticated)
            
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'], permission_classes=[ApproveAppPermission])     
    def update_pdf_status(self, request, slug=None):
        status = request.data['approve_status']
        remark = request.data['remark']
        PDFDoc.objects.filter(slug=slug).update(approve_status=status, 
                                                            approved_time=datetime.now(), 
                                                            approved_by=request.user, 
                                                            remark=remark)
        return Response({'status': 1})