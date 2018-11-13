from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'api'

urlpatterns = [
    path('app_list', views.AppListView.as_view(), name='app_list'),
    path('app_download_count', views.app_download_count, name="app_download_count"),
    path('get_video_upload_signature', views.get_video_upload_signature, name='get_video_upload_signature')
]

