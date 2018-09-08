from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_views

app_name = 'userauth'

urlpatterns = [
    path('sign_up', views.SignUpView.as_view(), name='signup'),
    path('sign_up_post', views.SignUpView.as_view(), name='signuppost'),
    path('logout', views.Logout.as_view(), name='logout'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', basic_views.others, name='others'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]