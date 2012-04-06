from django.conf.urls import patterns, url, include
from openduty.views import *

urlpatterns = patterns('',
	(r'^member/$', MemberListView.as_view()),
	(r'^event/$', EventListView.as_view()),
)