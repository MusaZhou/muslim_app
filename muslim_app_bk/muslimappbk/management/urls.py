from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_view
from .views import ImageFieldView, UpdateMobileAppView,  AppTableBasicView,\
AddAppVersionView, AppHistoryView, VersionDetailView
from .views_uploader import AppTableUploaderView, AppHistoryUploaderView
from .views import BannerListView, BannerEditView, BannerDeleteView
from django.views.decorators.cache import cache_page

app_name = 'management'

urlpatterns = [
    path('add_mobile_app', cache_page(24 * 60 * 60 * 15)(views.add_mobile_app), name='add_mobile_app'),
    path('add_app_images', ImageFieldView.as_view(), name='add_app_images'),
    path('update_mobile_app/<str:slug>', UpdateMobileAppView.as_view(), name='update_mobile_app'),
    path('add_app_version/<str:slug>', cache_page(24 * 60 * 60 * 15)(AddAppVersionView.as_view()), name='add_app_version'),
    path('app_table_basic', AppTableBasicView.as_view(), name='app_table_basic'),
    path('app_history/<str:slug>', AppHistoryView.as_view(), name='app_history'),
    path('app_table_uploader', AppTableUploaderView.as_view(), name='app_table_uploader'),
    path('app_history_uploader/<str:slug>', AppHistoryUploaderView.as_view(), name='app_history_uploader'),
    path('version_detail/<str:app_slug>-<str:version_number>', cache_page(24 * 60 * 60 * 15)(VersionDetailView.as_view()), name='version_detail'),
    path('update_version_status', views.update_version_status, name="update_version_status"),
    path('update_app_active', views.update_app_active, name="update_app_active"),
    path('upload_video', views.upload_video, name="upload_video"),
    path('upload_apk', views.upload_apk, name="upload_apk"),
    path('banner_list', BannerListView.as_view(), name="banner_list"),
    path('add_banner', cache_page(24 * 60 * 60 * 15)(BannerEditView.as_view()), name="add_banner"),
    path('edit_banner/<int:id>', BannerEditView.as_view(), name="edit_banner"),
    path('delete_banner/<int:id>', BannerDeleteView.as_view(), name="delete_banner"),
    path('index', views.index, name="index"),
]
