from django.views.generic import *
from django.forms import ModelForm
from django import forms
from openduty.models import *
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
import re

class MemberListView(ListView):
	model = Member
	template_name = "member/list.html"

class MemberDetailView(DetailView):
	model = Member
	template_name = "member/detail.html"

class MemberForm(ModelForm):
	email = forms.EmailField()

	class Meta:
		model = Member
		exclude = ('user',)

class MemberCreateView(CreateView):
	form_class = MemberForm
	template_name = "member/create.html"

	def form_valid(self, form):
		username = re.sub(r'\W', '', form.instance.name)
		email = form.cleaned_data['email']
		password = User.objects.make_random_password()

		user = User.objects.create_user(username, email, password)
		user.email_user("OpenDuty: User Created", render_to_string("member/create_email.html", {'username': username, 'password': password}))

		form.instance.user = user
		return super(MemberCreateView, self).form_valid(form)

class MemberUpdateView(UpdateView):
	model = Member
	form_class = MemberForm
	template_name = "member/update.html"

	def get_initial(self):
		initial = super(MemberUpdateView, self).get_initial()
		initial['email'] = self.get_object().user.email
		return initial

	def form_valid(self, form):
		email = form.cleaned_data['email']
		form.instance.user.email = email
		form.instance.user.save()

		return super(MemberUpdateView, self).form_valid(form)

class MemberDeleteView(DeleteView):
	model = Member
	template_name = "member/delete.html"

	def get_success_url(self):
		self.get_object().user.delete()
		return reverse('member')

class EventListView(ListView):
	model = Event
	template_name = "event/list.html"

class EventDetailView(DetailView):
	model = Event
	template_name = "event/detail.html"

class EventForm(ModelForm):
	class Meta:
		model = Event
		exclude = ('assignments',)
		widgets = {
			'begin': forms.SplitDateTimeWidget(),
			'end': forms.SplitDateTimeWidget(),
		}

class EventCreateView(CreateView):
	form_class = EventForm
	template_name = "event/create.html"

class EventUpdateView(UpdateView):
	model = Event
	form_class = EventForm
	template_name = "event/update.html"

class EventDeleteView(DeleteView):
	model = Event
	template_name = "event/delete.html"
	
	def get_success_url(self):
		return reverse('event')
