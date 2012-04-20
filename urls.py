from django.conf.urls import patterns, url, include
from openduty.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
	(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
	(r'^member/$', login_required(MemberListView.as_view())),
	(r'^event/$', login_required(EventListView.as_view())),
)