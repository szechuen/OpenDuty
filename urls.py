from django.conf.urls import patterns, url, include
from openduty.views import *
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
	(r'^accounts/profile/$', login_required(TemplateView.as_view(template_name="registration/profile.html"))),
	(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
	(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done'),
	(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset'),
	(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),
	(r'^accounts/password_reset_confirm/(?P<uidb36>\d+)/(?P<token>[\w-]+)/$', 'django.contrib.auth.views.password_reset_confirm'),
	(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete'),
	(r'^member/$', login_required(MemberListView.as_view())),
	(r'^event/$', login_required(EventListView.as_view())),
)