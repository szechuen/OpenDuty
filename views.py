from django.views.generic import *
from django.forms import ModelForm
from django import forms
from openduty.models import *
from django.contrib.auth.models import User
from actstream.models import Action
from actstream import action
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
import re

def mail_staff(subject, message):
	for user in User.objects.filter(is_staff=True):
		user.email_user(subject, message)

def mail_all(subject, message):
	for user in User.objects.all():
		user.email_user(subject, message)

class DashboardView(ListView):
	queryset = Action.objects.all()[:20]
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		context['pending_assignments'] = Assignment.objects.filter(status='Pending Approval', member=self.request.user.member)
		return context

class MemberListView(ListView):
	queryset = Member.objects.all().order_by('name')
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
		self.object.user.email_user("OpenDuty: Member Updated", render_to_string("member/update_email.html", {'member': self.object}))
		return super(MemberUpdateView, self).form_valid(form)

class MemberDeleteView(DeleteView):
	model = Member
	template_name = "member/delete.html"
	success_url = reverse_lazy('member')

	def get_object(self):
		object = super(MemberDeleteView, self).get_object()
		self.username = object.user.username
		return object

	def get_success_url(self):
		user = User.objects.get(username=self.username)
		user.email_user("OpenDuty: Member Deleted", render_to_string("member/delete_email.html"))
		user.delete()
		return super(MemberDeleteView, self).get_success_url()

class EventListView(ListView):
	template_name = "event/list.html"

	def get_queryset(self):
		return Event.objects.filter(end__gte=timezone.now()).order_by('begin')

class PastEventListView(ListView):
	template_name = "event/list_past.html"

	def get_queryset(self):
		return Event.objects.filter(end__lt=timezone.now()).order_by('-begin')

class EventDetailView(DetailView):
	model = Event
	template_name = "event/detail.html"

class EventForm(ModelForm):
	class Meta:
		model = Event
		exclude = ('assignments','reminder_sent')
		widgets = {
			'begin': forms.SplitDateTimeWidget(),
			'end': forms.SplitDateTimeWidget(),
		}

class EventCreateView(CreateView):
	form_class = EventForm
	template_name = "event/create.html"

	def form_valid(self, form):
		form.instance.reminder_sent = False

		self.object = form.save()
		action.send(self.request.user.member, verb='created', action_object=self.object)
		mail_all("OpenDuty: Event Created ("+self.object.name+")", render_to_string("event/create_email.html", {'event': self.object}))
		return super(EventCreateView, self).form_valid(form)

class EventUpdateView(UpdateView):
	model = Event
	form_class = EventForm
	template_name = "event/update.html"

	def form_valid(self, form):
		self.object = form.save()
		action.send(self.request.user.member, verb='updated', action_object=self.object)
		for assignment in self.object.assignment_set.filter(status="Approved"):
			assignment.member.user.email_user("OpenDuty: Event Updated ("+self.object.name+")", render_to_string("event/update_email.html", {'event': self.object}))
		return super(EventUpdateView, self).form_valid(form)

class EventDeleteView(DeleteView):
	model = Event
	template_name = "event/delete.html"
	success_url = reverse_lazy('event')

	def get_object(self):
		object = super(EventDeleteView, self).get_object()
		self.assigned_members = []
		for assignment in object.assignment_set.filter(status="Approved"):
			self.assigned_members.append(assignment.member)
		self.name = object.name
		return object

	def get_success_url(self):
		for member in self.assigned_members:
			member.user.email_user("OpenDuty: Event Deleted ("+self.name+")", render_to_string("event/delete_email.html", {'event_name': self.name}))
		return super(EventDeleteView, self).get_success_url()

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
		self.object.member.user.email_user("OpenDuty: Assigned to "+self.object.event.name, render_to_string("assignment/create_email.html", {'assignment': self.object}))
		return super(AssignmentCreateView, self).form_valid(form)

class AssignmentUpdateView(UpdateView):
	model = Assignment
	form_class = AssignmentForm
	template_name = "assignment/update.html"

	def form_valid(self, form):
		self.object = form.save()
		action.send(self.request.user.member, verb='updated', action_object=self.object, target=self.object.event)
		self.object.member.user.email_user("OpenDuty: Assignment Updated ("+self.object.event.name+")", render_to_string("assignment/update_email.html", {'assignment': self.object}))
		return super(AssignmentUpdateView, self).form_valid(form)

class AssignmentDeleteView(DeleteView):
	model = Assignment
	template_name = "assignment/delete.html"

	def get_object(self):
		object = super(AssignmentDeleteView, self).get_object()
		self.get_absolute_url = object.get_absolute_url()
		self.member = object.member
		self.event = object.event
		return object

	def get_success_url(self):
		self.member.user.email_user("OpenDuty: Assignment Deleted ("+self.event.name+")", render_to_string("assignment/delete_email.html", {'member': self.member, 'event': self.event}))
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
		mail_staff("OpenDuty: New Sign Up ("+str(self.object)+")", render_to_string("assignment/signup_email.html", {'assignment': self.object}))
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
	success_url = reverse_lazy('assignment_signup_queue')

	def form_valid(self, form):
		self.object = form.save()
		if self.object.status=='Approved':
			action.send(self.request.user.member, verb='approved', action_object=self.object, target=self.object.event)
			self.object.member.user.email_user("OpenDuty: Assignment Approved ("+self.object.event.name+")", render_to_string("assignment/signup_admin_email.html", {'assignment': self.object}))
		elif self.object.status=='Rejected':
			action.send(self.request.user.member, verb='rejected', action_object=self.object, target=self.object.event)
			self.object.member.user.email_user("OpenDuty: Assignment Rejected ("+self.object.event.name+")", render_to_string("assignment/signup_admin_email.html", {'assignment': self.object}))
		return super(SignUpAdminView, self).form_valid(form)
