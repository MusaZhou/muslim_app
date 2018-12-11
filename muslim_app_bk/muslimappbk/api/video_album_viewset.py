from rest_framework import status, viewsets
from management.models import VideoAlbum
from rest_framework.response import Response
from rest_framework.decorators import action
import json, logging
from rest_framework.permissions import IsAuthenticated
from .permissions import ApproveAppPermission
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoAlbumViewSet(viewsets.ModelViewSet):
    queryset = VideoAlbum.objects.all()
    lookup_field = 'slug'
    safe_actions = []
    
    def get_permissions(self):
        permission_classes = []
        if self.action not in self.safe_actions:
            permission_classes.append(IsAuthenticated)
            
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, slug=None):
        album = self.get_object()
        album.delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[ApproveAppPermission])     
    def update_video_album_status(self, request, slug=None):
        status = request.data['approve_status']
        remark = request.data['remark']
        now = datetime.now()
        checker = request.user
        VideoAlbum.objects.filter(slug=slug).update(approve_status=status, 
                                                            approved_time=now, 
                                                            approved_by=checker, 
                                                            remark=remark)
        data = {'time': now.strftime('%m-%d-%Y %H:%M'), 'checker': checker.username, 'status': status}
        return Response(data)