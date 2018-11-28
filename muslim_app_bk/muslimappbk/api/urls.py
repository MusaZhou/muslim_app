from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'api'

urlpatterns = [
    path('app_list', views.AppListView.as_view(), name='app_list'),
    path('app_download_count', views.app_download_count, name="app_download_count"),
    path('get_video_upload_signature', views.get_video_upload_signature, name='get_video_upload_signature'),
    path('process_video_notify', views.process_video_notify, name='process_video_notify'),
    path('notify_video_process_task', views.notify_video_process_task, name='notify_video_process_task'),
    path('get_image_upload_signature', views.get_image_upload_signature, name='get_image_upload_signature'),
    path('notify_image_process_task', views.notify_image_process_task, name='notify_image_process_task'),
    path('image_thumbnail_notify', views.image_thumbnail_notify, name='image_thumbnail_notify'),
    path('process_video_thumbnail_notify', views.process_video_thumbnail_notify, name="process_video_thumbnail_notify"),
    path('inspired_video_list', views.InspiredVideoListView.as_view(), name="inspired_video_list")
]

