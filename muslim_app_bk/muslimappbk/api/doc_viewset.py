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
    safe_actions = []
    
    def get_permissions(self):
        permission_classes = []
        if self.action not in self.safe_actions:
            permission_classes.append(IsAuthenticated)
            
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, slug=None):
        pdf = self.get_object()
        pdf.delete()
        return Response(status=status.HTTP_200_OK)
    
    
    
    @action(detail=True, methods=['post'], permission_classes=[ApproveAppPermission])     
    def update_pdf_status(self, request, slug=None):
        status = request.data['approve_status']
        remark = request.data['remark']
        now = datetime.now()
        checker = request.user
        PDFDoc.objects.filter(slug=slug).update(approve_status=status, 
                                                approved_time=now, 
                                                approved_by=checker, 
                                                remark=remark)
        data = {'time': now.strftime('%m-%d-%Y %H:%M'), 'checker': checker.username, 'status': status}
        return Response(data)