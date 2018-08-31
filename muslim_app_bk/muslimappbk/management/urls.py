from django.urls import path, include
from django.conf import settings
from . import views

app_name = 'management'

urlpatterns = [
    path('404', basic_views.page_404, name='404'),
    path('500', basic_views.page_500, name='500'),
    path('datatable', basic_views.datatable, name='datatable'),
    path('forms', basic_views.forms, name='forms'),
    path('signin', basic_views.signin, name='signin'),
    path('signup', basic_views.signup, name='signup'),
    path('index', basic_views.index, name='index'),
    path('<str:characters>', basic_views.others, name='others')
]