from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'showcase'

urlpatterns = [
    path('blog_template/', views.blog_template, name='blog_template'),
    path('dashboard_template/', views.dashboard_template, name='dashboard_template')
]

