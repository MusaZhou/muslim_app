from rest_framework import status, viewsets
from .serializers import AppSerializer
from management.models import MobileApp, AppVersion
from django.core.paginator import InvalidPage, Paginator
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F
from .permissions import ApproveAppPermission
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

class AppViewSet(viewsets.ModelViewSet):
    serializer_class = AppSerializer
    queryset = MobileApp.objects.all()
    lookup_field = 'slug'
    safe_actions = ['list', 'download_count']
    
    def get_permissions(self):
        permission_classes = []
        if self.action not in self.safe_actions:
            permission_classes.append(IsAuthenticated)
            
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        category_id = int(request.query_params.get('cate_id', 9999))
        page = int(self.request.query_params.get('page', 1))
        
        if category_id == 9999:
            mobile_list_all = MobileApp.shown_apps.all()
        else:    
            mobile_list_all = MobileApp.shown_apps.filter(category__id=category_id)
            
        paginator = Paginator(mobile_list_all, 9)
        try:
            mobile_list = paginator.page(page)
            serializer = AppSerializer(mobile_list.object_list, many=True)
        except InvalidPage:
            serializer = AppSerializer(MobileApp.objects.none(), many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def download_count(self, request, slug=None):
        MobileApp.objects.filter(slug=slug).update(download_count=F('download_count')+1)
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[ApproveAppPermission])    
    def update_version_status(self, request, slug=None):
        app_version_number = request.data['version_number']
        status = request.data['approve_status']
        remark = request.data['remark']
        app = self.get_object()
        now = datetime.now()
        checker = request.user
        
        AppVersion.objects.filter(mobile_app=app, version_number=app_version_number)\
        .update(approve_status=status, 
                approved_time=now, 
                approved_by=checker, 
                remark=remark)
        data = {'time': now.strftime('%m-%d-%Y %H:%M'), 'checker': checker.username, 'status': status}
        return Response(data)