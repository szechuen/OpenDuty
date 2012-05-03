from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
	user = models.OneToOneField(User)

	name = models.CharField(max_length=50)
	class_name = models.CharField(max_length=20)
	
	home_phone = models.CharField(max_length=20)
	mobile_phone = models.CharField(max_length=20)

	facebook = models.CharField(max_length=50, blank=True)

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('member_detail', [str(self.id)])

class Event(models.Model):
	name = models.CharField(max_length=50)

	begin = models.DateTimeField()
	end = models.DateTimeField()
	def duration(self):
		return (self.end-self.begin).total_seconds()/3600
	def cip_duration(self):
		if self.cip: 
			return self.duration()
		else:
			return 0
	venue = models.CharField(max_length=20)

	audio_visual = models.BooleanField()
	photo = models.BooleanField()
	video = models.BooleanField()
	cip = models.BooleanField("CIP")

	remarks = models.TextField(blank=True)

	assignments = models.ManyToManyField(Member, through="Assignment")
	reminder_sent = models.BooleanField()

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('event_detail', [str(self.id)])

class Assignment(models.Model):
	member = models.ForeignKey(Member)
	event = models.ForeignKey(Event)

	TYPE_CHOICES = (
		('Audio-Visual', 'Audio-Visual'),
		('Photo', 'Photo'),
		('Video', 'Video')
	)
	type = models.CharField(max_length=20, choices=TYPE_CHOICES)

	STATUS_CHOICES = (
		('Pending Approval', 'Pending Approval'),
		('Approved', 'Approved'),
		('Rejected', 'Rejected')
	)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	remarks = models.TextField(blank=True)

	def __unicode__(self):
		return self.member.name + " >> " + self.event.name

	@models.permalink
	def get_absolute_url(self):
		return ('event_detail', [str(self.event.id)])
