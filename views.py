from django.views.generic import *
from openduty.models import *

class MemberListView(ListView):
	model = Member
	template_name = "member_list.html"