from django.urls import path, include, re_path
from django.conf import settings
from . import views
from basic import views as basic_views
from django.views.decorators.cache import cache_page

app_name = 'userauth'

urlpatterns = [
    path('sign_up', cache_page(24 * 60 * 60 * 15)(views.SignUpView.as_view()), name='signup'),
    path('sign_up_post', views.SignUpView.as_view(), name='signuppost'),
    path('login', cache_page(24 * 60 * 60 * 15)(views.UserauthLoginView.as_view()), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('update_profile', views.UpdateProfileView.as_view(), name="update_profile"),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]