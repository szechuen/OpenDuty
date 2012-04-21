from django.conf.urls import patterns, url, include
from openduty.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
	(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
	(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done'),
	(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset'),
	(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),
	(r'^accounts/password_reset_confirm/$', 'django.contrib.auth.views.password_reset_confirm'),
	(r'^member/$', login_required(MemberListView.as_view())),
	(r'^event/$', login_required(EventListView.as_view())),
)