from django.views.generic import *
from openduty.models import *

class MemberListView(ListView):
	model = Member
	template_name = "member/list.html"

class MemberDetailView(DetailView):
	model = Member
	template_name = "member/detail.html"

class EventListView(ListView):
	model = Event
	template_name = "event/list.html"
