from rest_framework import status, viewsets
from .serializers import InspiredVideoSerializer
from management.models import InspiredVideo
from django.core.paginator import InvalidPage, Paginator
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F
import json, logging
from rest_framework.permissions import IsAuthenticated
from .permissions import ApproveAppPermission
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = InspiredVideoSerializer
    queryset = InspiredVideo.objects.all()
    lookup_field = 'slug'
    safe_actions = ['list', 'view_count']
    
    def get_permissions(self):
        permission_classes = []
        if self.action not in self.safe_actions:
            permission_classes.append(IsAuthenticated)
            
        return [permission() for permission in permission_classes]
    
    def list(self, request):
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
            serializer =  InspiredVideoSerializer(video_list.object_list, many=True)
        except InvalidPage:
            serializer =  InspiredVideoSerializer(InspiredVideo.objects.none(), many=True)
        
        return Response(serializer.data)
    
    def destroy(self, request, slug=None):
        video = self.get_object()
        video.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def view_count(self, request, slug=None):
        InspiredVideo.objects.filter(slug=slug).update(view_count=F('view_count')+1)
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[ApproveAppPermission])     
    def update_video_status(self, request, slug=None):
        status = request.data['approve_status']
        remark = request.data['remark']
        now = datetime.now()
        checker = request.user
        InspiredVideo.objects.filter(slug=slug).update(approve_status=status, 
                                                            approved_time=now, 
                                                            approved_by=checker, 
                                                            remark=remark)
        data = {'time': now.strftime('%m-%d-%Y %H:%M'), 'checker': checker.username, 'status': status}
        return Response(data)