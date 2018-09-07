from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_views

app_name = 'userauth'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', basic_views.others, name='others'),
]