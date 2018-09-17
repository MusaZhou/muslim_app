from django.shortcuts import render
from rest_framework.views import APIView
from management.models import MobileApp
from api.serializers import AppSerializer
from rest_framework.response import Response

class AppListView(APIView):
 
    def get(self, request, *args, **kwargs):
        app_list = MobileApp.objects.filter(category__id=kwargs['cate_id'])
        serializer = AppSerializer(app_list, many=True)
        return Response(serializer.data)