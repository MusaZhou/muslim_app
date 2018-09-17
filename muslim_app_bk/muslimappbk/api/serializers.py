from rest_framework import serializers
from management.models import MobileApp

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileApp
        fields = ('name', 'description', 'icon', 'slug')