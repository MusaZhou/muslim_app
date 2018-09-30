from django.urls import path, include, re_path
from django.conf import settings
from . import views
from django_comments_xtd import views as comments_view

app_name = 'mobile'

urlpatterns = [
    path('blog_template/', views.blog_template, name='blog_template'),
    path('dashboard_template/', views.dashboard_template, name='dashboard_template'),
    path('carousel_template/', views.carousel_template, name='carousel_template'),
    path('album_template/', views.album_template, name='album_template'),
    path('index/', views.index, name='index'),
    path('app/<slug:slug>', views.app, name='app'),
    path('reply/<int:cid>/<slug:app_slug>', views.reply, name='reply'),
]
