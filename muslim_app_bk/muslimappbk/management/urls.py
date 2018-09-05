from django.urls import path, include, re_path
from django.conf import settings
from . import views, basic_views
from .views import ImageFieldView, UpdateMobileAppView, AppTableBasicView, AddAppVersionView

app_name = 'management'

urlpatterns = [
    path('404', basic_views.page_404, name='404'),
    path('500', basic_views.page_500, name='500'),
    path('datatable', basic_views.datatable, name='datatable'),
    path('forms', basic_views.forms, name='forms'),
    path('ui', basic_views.ui, name='ui'),
    path('signin', basic_views.signin, name='signin'),
    path('signup', basic_views.signup, name='signup'),
    path('index', basic_views.index, name='index'),
    path('add_mobile_app', views.add_mobile_app, name='add_mobile_app'),
    path('logger', basic_views.customLogger, name='logger'),
    path('add_app_images', ImageFieldView.as_view(), name='add_app_images'),
    path('update_mobile_app/<slug:slug>', UpdateMobileAppView.as_view(), name='update_mobile_app'),
    path('add_app_version/<slug:slug>', AddAppVersionView.as_view(), name='add_app_version'),
    path('app_table_basic', AppTableBasicView.as_view(), name='app_table_basic'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', basic_views.others, name='others')
]
