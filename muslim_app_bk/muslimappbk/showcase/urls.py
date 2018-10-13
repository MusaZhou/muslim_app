from django.urls import path, include, re_path
from django.conf import settings
from . import views
from django.views.decorators.cache import cache_page

app_name = 'showcase'

urlpatterns = [
#     path('blog_template/', views.blog_template, name='blog_template'),
#     path('dashboard_template/', views.dashboard_template, name='dashboard_template'),
#     path('carousel_template/', views.carousel_template, name='carousel_template'),
#     path('album_template/', views.album_template, name='album_template'),
    path('index/', cache_page(24 * 60 * 60 * 15)(views.index, name='index')),
    path('app/<str:slug>', cache_page(60 * 60 * 15)(views.app), name='app'),
    path('search', views.search, name="search")
]

