"""muslimappbk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.conf import settings
from . import views

app_name = 'basic'

urlpatterns = [
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('index', views.index, name='index'),
    path('404', views.page_404, name='404'),
    path('500', views.page_500, name='500'),
    path('datatable', views.datatable, name='datatable'),
    path('forms', views.forms, name='forms'),
    path('ui', views.ui, name='ui'),
    path('logger', views.customLogger, name='logger'),
    re_path(r'(?P<file>(\w*\.(eot|svg|woff|woff2|ttf))$)', views.others, name='others'),
]

