from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'api'

urlpatterns = [
    path('app_list', views.AppListView.as_view(), name='app_list'),
]

