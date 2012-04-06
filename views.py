from django.views.generic import *
from openduty.models import *

class MemberListView(ListView):
	model = Member
	template_name = "member_list.html"

class EventListView(ListView):
	model = Event
	template_name = "event_list.html"