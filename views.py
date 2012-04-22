from django.views.generic import *
from openduty.models import *

class MemberListView(ListView):
	model = Member
	template_name = "member/list.html"

class EventListView(ListView):
	model = Event
	template_name = "event/list.html"