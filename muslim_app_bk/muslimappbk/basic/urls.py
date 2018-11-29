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
    path('email', views.email, name='email'),
    path('test', views.test, name='test'),
    path('test_view', views.test_view, name="test_view"),
]

