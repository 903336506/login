#Embedded file name: ./login/bkaccount/urls.py
from bkaccount import views
from django.conf.urls import url
urlpatterns = [url('^$', views.users, name='users'),
 url('^get_info/$', views.get_info, name='get_info'),
 url('^save_user/$', views.save_user, name='save_user'),
 url('^del_user/$', views.del_user, name='del_user'),
 url('^change_password/$', views.change_password, name='change_password'),
 url('^import_data/$', views.import_data, name='import_data'),
 url('^export_data/$', views.export_data, name='export_data'),
 url('^is_login/$', views.is_login, name='is_login'),
 url('^get_user/$', views.get_user, name='get_user'),
 url('^get_all_user/$', views.get_all_user, name='get_all_user'),
 url('^get_batch_user/$', views.get_batch_user, name='get_batch_user'),
 url('^reset_password/$', views.reset_password, name='reset_password'),
 url('^modify_user_info/$', views.modify_user_info, name='modify_user_info')]
