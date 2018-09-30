from django.urls import path, include, re_path
from django.conf import settings
from . import views
from django_comments_xtd import views as comments_view

app_name = 'mobile'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('app/<slug:slug>', views.app, name='app'),
    path('reply/<int:cid>/<slug:app_slug>', views.reply, name='reply'),
]

