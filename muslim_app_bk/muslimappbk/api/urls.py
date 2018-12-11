from django.urls import path, include, re_path
from django.conf import settings
from . import views, common_apiview
from rest_framework import routers
from .app_viewset import AppViewSet
from .doc_viewset import DocViewSet
from .video_viewset import VideoViewSet
from .video_album_viewset import VideoAlbumViewSet
from .banner_viewset import BannerViewSet

app_name = 'api'

# urlpatterns = [
#     path('app_list', views.AppListView.as_view(), name='app_list'),
#     path('app_download_count', views.app_download_count, name="app_download_count"),
#     path('get_video_upload_signature', views.get_video_upload_signature, name='get_video_upload_signature'),
#     path('process_video_notify', views.process_video_notify, name='process_video_notify'),
#     path('notify_video_process_task', views.notify_video_process_task, name='notify_video_process_task'),
#     path('get_image_upload_signature', views.get_image_upload_signature, name='get_image_upload_signature'),
#     path('notify_image_process_task', views.notify_image_process_task, name='notify_image_process_task'),
#     path('image_thumbnail_notify', views.image_thumbnail_notify, name='image_thumbnail_notify'),
#     path('process_video_thumbnail_notify', views.process_video_thumbnail_notify, name="process_video_thumbnail_notify"),
#     path('inspired_video_list', views.InspiredVideoListView.as_view(), name="inspired_video_list"),
#     path('get_file_upload_signature', views.get_file_upload_signature, name="get_file_upload_signature")
# ]

router = routers.DefaultRouter()
router.register('apps', AppViewSet, 'app')
router.register('docs', DocViewSet, 'doc')
router.register('videos', VideoViewSet, 'video')
router.register('video_albums', VideoAlbumViewSet, 'video-album')
router.register('banners', BannerViewSet, 'banner')

urlpatterns = router.urls

common_urlpatterns = [
    path('get_video_upload_signature', common_apiview.get_video_upload_signature, name='get_video_upload_signature'),
    path('process_video_notify', common_apiview.process_video_notify, name='process_video_notify'),
    path('notify_video_process_task', common_apiview.notify_video_process_task, name='notify_video_process_task'),
    path('get_image_upload_signature', common_apiview.get_image_upload_signature, name='get_image_upload_signature'),
    path('notify_image_process_task', common_apiview.notify_image_process_task, name='notify_image_process_task'),
    path('image_thumbnail_notify', common_apiview.image_thumbnail_notify, name='image_thumbnail_notify'),
    path('process_video_thumbnail_notify', common_apiview.process_video_thumbnail_notify, name="process_video_thumbnail_notify"),
    path('get_file_upload_signature', common_apiview.get_file_upload_signature, name="get_file_upload_signature")
]

urlpatterns += common_urlpatterns

