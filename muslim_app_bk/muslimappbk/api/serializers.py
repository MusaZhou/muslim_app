from rest_framework import serializers
from management.models import MobileApp, InspiredVideo

class AppSerializer(serializers.ModelSerializer):
    apk = serializers.CharField(source='latestAPK', read_only=True)
    url = serializers.CharField(source='userLink', read_only=True)
    url_mobile = serializers.CharField(source='user_link_mobile', read_only=True)
    time = serializers.DateTimeField(source='latestTime', format="%Y/%m/%d", read_only=True)
    
    class Meta:
        model = MobileApp
        fields = ('name', 'description', 'icon', 'slug', 'apk', 'url', 'url_mobile', 'avg_rate', 'time')
        
class InspiredVideoSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='userLink', read_only=True)
    url_mobile = serializers.CharField(source='user_link_mobile', read_only=True)
    video_duration = serializers.CharField(source='video_duration_str', read_only=True)
    
    class Meta:
        model = InspiredVideo
        fields = ('title', 'slug', 'view_count', 'thumbnail_path', 'url', 'url_mobile', 'video_duration')