from django.views.generic import *
from django.forms import ModelForm
from django import forms
from openduty.models import *
from django.contrib.auth.models import User
from actstream.models import Action
from actstream import action
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
import re

class DashboardView(ListView):
	queryset = Action.objects.all()[:20]
	template_name = "dashboard.html"

class MemberListView(ListView):
	model = Member
	template_name = "member/list.html"

class MemberDetailView(DetailView):
	model = Member
	template_name = "member/detail.html"

	def get_context_data(self, **kwargs):
		context = super(MemberDetailView, self).get_context_data(**kwargs)
		context['total_duration'] = 0
		context['total_cip_duration'] = 0
		for assignment in context['member'].assignment_set.all():
			context['total_duration'] += assignment.event.duration()
			context['total_cip_duration'] += assignment.event.cip_duration()
		return context

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
		self.object = form.save()
		action.send(self.request.user.member, verb='created', action_object=self.object)
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

		self.object = form.save()
		action.send(self.request.user.member, verb='updated', action_object=self.object)
		return super(MemberUpdateView, self).form_valid(form)

class MemberDeleteView(DeleteView):
	model = Member
	template_name = "member/delete.html"

	def get_object(self):
		object = super(MemberDeleteView, self).get_object()
		self.username = object.user.username
		return object

	def get_success_url(self):
		User.objects.get(username=self.username).delete()
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

	def form_valid(self, form):
		self.object = form.save()
		action.send(self.request.user.member, verb='created', action_object=self.object)
		return super(EventCreateView, self).form_valid(form)

class EventUpdateView(UpdateView):
	model = Event
	form_class = EventForm
	template_name = "event/update.html"

	def form_valid(self, form):
		self.object = form.save()
		action.send(self.request.user.member, verb='updated', action_object=self.object)
		return super(EventUpdateView, self).form_valid(form)

class EventDeleteView(DeleteView):
	model = Event
	template_name = "event/delete.html"
	
	def get_success_url(self):
		return reverse('event')

class AssignmentForm(ModelForm):
	class Meta:
		model = Assignment
		exclude = ('event','status',)

class AssignmentCreateView(CreateView):
	form_class = AssignmentForm
	template_name = "assignment/create.html"

	def get_context_data(self, **kwargs):
		context = super(AssignmentCreateView, self).get_context_data(**kwargs)
		context['event'] = Event.objects.get(id=self.kwargs['event_pk'])
		return context

	def form_valid(self, form):
		form.instance.event = Event.objects.get(id=self.kwargs['event_pk'])
		form.instance.status = 'Approved'

		self.object = form.save()
		action.send(self.request.user.member, verb='assigned', action_object=self.object, target=self.object.event)
		return super(AssignmentCreateView, self).form_valid(form)

class AssignmentUpdateView(UpdateView):
	model = Assignment
	form_class = AssignmentForm
	template_name = "assignment/update.html"

	def form_valid(self, form):
		self.object = form.save()
		action.send(self.request.user.member, verb='updated', action_object=self.object, target=self.object.event)
		return super(AssignmentUpdateView, self).form_valid(form)

class AssignmentDeleteView(DeleteView):
	model = Assignment
	template_name = "assignment/delete.html"

	def get_object(self):
		object = super(AssignmentDeleteView, self).get_object()
		self.get_absolute_url = object.get_absolute_url()
		return object

	def get_success_url(self):
		return self.get_absolute_url

class SignUpForm(ModelForm):
	class Meta:
		model = Assignment
		exclude = ('member','event','status',)

class SignUpView(CreateView):
	form_class = SignUpForm
	template_name = "assignment/signup.html"

	def get_context_data(self, **kwargs):
		context = super(SignUpView, self).get_context_data(**kwargs)
		context['event'] = Event.objects.get(id=self.kwargs['event_pk'])
		return context

	def form_valid(self, form):
		form.instance.member = self.request.user.member
		form.instance.event = Event.objects.get(id=self.kwargs['event_pk'])
		form.instance.status = 'Pending Approval'

		self.object = form.save()
		action.send(self.request.user.member, verb='signed up for', action_object=self.object, target=self.object.event)
		return super(SignUpView, self).form_valid(form)

class SignUpQueueView(ListView):
	queryset = Assignment.objects.filter(status='Pending Approval')
	template_name = "assignment/signup_queue.html"

class SignUpAdminForm(ModelForm):
	class Meta:
		model = Assignment
		fields = ('status',)

class SignUpAdminView(UpdateView):
	model = Assignment
	form_class = SignUpAdminForm
	template_name = "assignment/signup_admin.html"

	def form_valid(self, form):
		self.object = form.save()
		if self.object.status=='Approved':
			action.send(self.request.user.member, verb='approved', action_object=self.object, target=self.object.event)
		elif self.object.status=='Rejected':
			action.send(self.request.user.member, verb='rejected', action_object=self.object, target=self.object.event)
		return super(SignUpAdminView, self).form_valid(form)

	def get_success_url(self):
		return reverse('assignment_signup_queue')
