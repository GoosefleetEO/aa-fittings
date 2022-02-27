from django.urls import re_path

from . import views

app_name = 'fittings'

urlpatterns = [
    re_path(r'^$', views.dashboard, name='dashboard'),
    re_path(r'^fit/add/$', views.add_fit, name='add_fit'),
    re_path(r'^fit/all/$', views.view_all_fits, name='view_all_fits'),
    re_path(r'^fit/(?P<fit_id>[0-9]+)/$', views.view_fit, name='view_fit'),
    re_path(r'^fit/(?P<fit_id>[0-9]+)/delete/$', views.delete_fit, name='delete_fit'),
    re_path(r'^fit/(?P<fit_id>[0-9]+)/save/$', views.save_fit, name='save_fit'),
    re_path(r'^fit/(?P<fit_id>[0-9]+)/edit/$', views.edit_fit, name='edit_fit'),
    re_path(r'^doctrine/add/$', views.add_doctrine, name='add_doctrine'),
    re_path(r'^doctrine/(?P<doctrine_id>[0-9]+)/$', views.view_doctrine, name='view_doctrine'),
    re_path(r'^doctrine/(?P<doctrine_id>[0-9]+)/delete/$', views.delete_doctrine, name='delete_doctrine'),
    re_path(r'^doctrine/(?P<doctrine_id>[0-9]+)/edit/$', views.edit_doctrine, name='edit_doctrine'),
    re_path(r'^cat/all/$', views.view_all_categories, name='view_all_categories'),
    re_path(r'^cat/add/$', views.add_category, name='add_category'),
    re_path(r'^cat/(?P<cat_id>[0-9]+)/$', views.view_category, name='view_category'),
    re_path(r'^cat/(?P<cat_id>[0-9]+)/edit/$', views.edit_category, name='edit_category'),
    re_path(r'^cat/(?P<cat_id>[0-9]+)/delete/$', views.delete_category, name='delete_category'),
]
