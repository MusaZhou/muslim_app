from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_views
from .views import SignUpView

app_name = 'userauth'

urlpatterns = [
    path('sign_up', SignUpView.as_view(), name='signup'),
    path('sign_up_post', SignUpView.as_view(), name='signuppost'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', basic_views.others, name='others'),
]