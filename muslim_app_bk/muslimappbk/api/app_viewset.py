from rest_framework import status, viewsets
from .serializers import AppSerializer
from management.models import MobileApp
from django.core.paginator import InvalidPage, Paginator
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F

class AppViewSet(viewsets.ModelViewSet):
    serializer_class = AppSerializer
    queryset = MobileApp.objects.all()
    lookup_field = 'slug'
    
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
            serializer = AppSerializer(data=mobile_list.object_list)
        except InvalidPage:
            serializer = AppSerializer(MobileApp.objects.none()).initial_data
        
        if serializer.is_valid():
            return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def app_download_count(self, request, slug=None):
        MobileApp.objects.filter(slug=slug).update(download_count=F('download_count')+1)
        return Response(status=status.HTTP_200_OK)