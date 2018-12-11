from rest_framework import status, viewsets
from management.models import Banner
from rest_framework.response import Response
from .permissions import ApproveAppPermission
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    safe_actions = []
    
    def get_permissions(self):
        permission_classes = []
        if self.action not in self.safe_actions:
            permission_classes.append(ApproveAppPermission)
            
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, pk=None):
        banner = self.get_object()
        banner.delete()
        return Response(status=status.HTTP_200_OK)