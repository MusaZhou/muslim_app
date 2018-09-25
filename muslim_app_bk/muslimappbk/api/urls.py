from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'api'

urlpatterns = [
    path('app_list', views.AppListView.as_view(), name='app_list'),
    path('app_download_count', views.app_download_count, name="app_download_count"),
    path('upyun_sign_head', views.upyun_sign_head, name='upyun_sign_head')
]

