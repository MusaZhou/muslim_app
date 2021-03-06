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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from basic import views as basic_view
from userauth import views as userauth_view

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('management/', include('management.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('basic/', include('basic.urls')),
    path('userauth/', include('userauth.urls')),
    path('accounts/', include('allauth.urls')),
    path('showcase/', include('showcase.urls')),
    path('comments/', include('django_comments_xtd.urls')),
    path('api/', include('api.urls')),
    path('mobile/', include('mobile.urls')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('i18n/', include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += [
        path('__debug__', include(debug_toolbar.urls)),
    ]
    

# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']
