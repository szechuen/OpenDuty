from django.conf.urls import patterns, url, include
from openduty.views import *
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
	url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
	url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
	url(r'^accounts/profile/$', login_required(TemplateView.as_view(template_name="registration/profile.html")), name='accounts_profile'),
	url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
	url(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done'),
	url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset'),
	url(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),
	url(r'^accounts/password_reset_confirm/(?P<uidb36>\d+)/(?P<token>[\w-]+)/$', 'django.contrib.auth.views.password_reset_confirm'),
	url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete'),
	url(r'^member/$', login_required(MemberListView.as_view()), name='member'),
	url(r'^member/detail/(?P<pk>\d+)/$', login_required(MemberDetailView.as_view()), name='member_detail'),
	url(r'^event/$', login_required(EventListView.as_view()), name='event'),
	url(r'^event/detail/(?P<pk>\d+)/$', login_required(EventDetailView.as_view()), name='event_detail'),
)
