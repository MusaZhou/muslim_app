from django.urls import path, include
from django.conf import settings
from . import views

app_name = 'management'

urlpatterns = [
    path('404', views.page_404, name='404'),
    path('500', views.page_500, name='500'),
    path('datatable', views.datatable, name='datatable'),
    path('forms', views.forms, name='forms'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('<str:characters>', views.others, name='others')
]
