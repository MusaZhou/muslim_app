from django.urls import path, include, re_path
from django.conf import settings
from . import views
from django_comments_xtd import views as comments_view
from django.views.decorators.cache import cache_page

app_name = 'mobile'

urlpatterns = [
    path('index/', cache_page(24 * 60 * 60 * 15)(views.index), name='index'),
    path('app/<str:slug>', cache_page(60 * 15)(views.app), name='app'),
    path('reply/<int:cid>/<str:app_slug>', views.reply, name='reply'),
    path('search', views.search, name="search")
]

