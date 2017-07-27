#Embedded file name: ./login/urls.py
"""paas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from bkaccount import views as account_views
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
urlpatterns = [url('^$', account_views.login),
 url('^logout/$', account_views.logout),
 url('^accounts/', include('bkaccount.urls')),
 url('^admin/', include(admin.site.urls)),
 url('^login/accounts/is_login/$', account_views.is_login),
 url('^login/accounts/get_user/$', account_views.get_user),
 url('^login/accounts/get_all_user/$', account_views.get_all_user),
 url('^login/accounts/get_batch_user/$', account_views.get_batch_user),
 url('^login/accounts/reset_password/$', account_views.reset_password),
 url('^login/accounts/modify_user_info/$', account_views.modify_user_info),
 url('^robots\\.txt$', lambda r: HttpResponse('User-agent: *\nDisallow: /', content_type='text/plain'))]
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
