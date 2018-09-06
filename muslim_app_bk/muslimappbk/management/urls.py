from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_view
from .views import ImageFieldView, UpdateMobileAppView,  AppTableBasicView,  AddAppVersionView, AppHistoryView

app_name = 'management'

urlpatterns = [
    path('add_mobile_app', views.add_mobile_app, name='add_mobile_app'),
    path('add_app_images', ImageFieldView.as_view(), name='add_app_images'),
    path('update_mobile_app/<slug:slug>', UpdateMobileAppView.as_view(), name='update_mobile_app'),
    path('add_app_version/<slug:slug>', AddAppVersionView.as_view(), name='add_app_version'),
    path('app_table_basic', AppTableBasicView.as_view(), name='app_table_basic'),
    path('app_history/<slug:slug>', AppHistoryView.as_view(), name='app_history'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', basic_view.others, name='others'),
]
