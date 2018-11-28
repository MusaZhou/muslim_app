from django.urls import path, include, re_path
from django.conf import settings
from . import views
from django.views.decorators.cache import cache_page

app_name = 'showcase'

urlpatterns = [
    path('index/', cache_page(24 * 60 * 60 * 15)(views.index), name='index'),
    path('app/<str:slug>', cache_page(60 * 60 * 15)(views.app), name='app'),
    path('search', views.search, name="search"),
    path('disqus', views.disqus, name="disqus"),
    path('index_pdf/', views.index_pdf, name="index_pdf"),
    path('detail_pdf/<str:slug>', views.detail_pdf, name="detail_pdf"),
    path('index_inspired_video', views.index_inspired_video, name="index_inspired_video"),
    path('detail_inspired_video/<str:slug>', views.detail_inspired_video, name="detail_inspired_video")
]

