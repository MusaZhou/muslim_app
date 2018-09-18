
from management.models import MobileApp
from api.serializers import AppSerializer
from rest_framework import generics

class AppListView(generics.ListAPIView):
    serializer_class = AppSerializer
    
    def get_queryset(self):
        category_id = int(self.request.query_params.get('cate_id', 9999))
        if category_id == 9999:
            return MobileApp.objects.all()
        return MobileApp.objects.filter(category__id=category_id)