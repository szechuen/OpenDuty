from django.conf.urls import patterns, url, include
from openduty.views import *
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
	url(r'^$', RedirectView.as_view(url=reverse_lazy('dashboard'), permanent=False), name='root'),
	url(r'^dashboard/$', login_required(DashboardView.as_view()), name='dashboard'),

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
	url(r'^member/create/$', user_passes_test(lambda u: u.is_staff)(MemberCreateView.as_view()), name='member_create'),
	url(r'^member/update/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(MemberUpdateView.as_view()), name='member_update'),
	url(r'^member/delete/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(MemberDeleteView.as_view()), name='member_delete'),
	
	url(r'^event/$', login_required(EventListView.as_view()), name='event'),
	url(r'^event/past/$', login_required(PastEventListView.as_view()), name='event_past'),
	url(r'^event/detail/(?P<pk>\d+)/$', login_required(EventDetailView.as_view()), name='event_detail'),
	url(r'^event/create/$', user_passes_test(lambda u: u.is_staff)(EventCreateView.as_view()), name='event_create'),
	url(r'^event/update/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(EventUpdateView.as_view()), name='event_update'),
	url(r'^event/delete/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(EventDeleteView.as_view()), name='event_delete'),

	url(r'^assignment/create/event/(?P<event_pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(AssignmentCreateView.as_view()), name='assignment_create'),
	url(r'^assignment/update/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(AssignmentUpdateView.as_view()), name='assignment_update'),
	url(r'^assignment/delete/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(AssignmentDeleteView.as_view()), name='assignment_delete'),
	url(r'^assignment/signup/event/(?P<event_pk>\d+)/$', login_required(SignUpView.as_view()), name='assignment_signup'),
	url(r'^assignment/signup/queue/$', user_passes_test(lambda u: u.is_staff)(SignUpQueueView.as_view()), name='assignment_signup_queue'),
	url(r'^assignment/signup/admin/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_staff)(SignUpAdminView.as_view()), name='assignment_signup_admin'),

	url(r'^facebook/$', 'openduty.views.facebook', name='facebook'),
)
