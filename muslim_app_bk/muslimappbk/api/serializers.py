from rest_framework import serializers
from management.models import MobileApp

class AppSerializer(serializers.ModelSerializer):
    apk = serializers.CharField(source='latestAPK', read_only=True)
    url = serializers.CharField(source='userLink', read_only=True)
    url_mobile = serializers.CharField(source='user_link_mobile', read_only=True)
    time = serializers.DateTimeField(source='latestTime', format="%Y/%m/%d", read_only=True)
    
    class Meta:
        model = MobileApp
        fields = ('name', 'description', 'icon', 'slug', 'apk', 'url', 'url_mobile', 'avg_rate', 'time')