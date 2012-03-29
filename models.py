from django.db import models

class Member(models.Model):
	name = models.CharField(max_length=50)
	class_name = models.CharField(max_length=20)
	
	home_phone = models.CharField(max_length=20)
	mobile_phone = models.CharField(max_length=20)
	email = models.EmailField()

	def __unicode__(self):
		return self.name

class Event(models.Model):
	name = models.CharField(max_length=50)

	begin = models.DateTimeField()
	end = models.DateTimeField()
	venue = models.CharField(max_length=20)

	remarks = models.TextField(blank=True)

	assignments = models.ManyToManyField(Member, through="Assignment")

	def __unicode__(self):
		return self.name

class Assignment(models.Model):
	member = models.ForeignKey(Member)
	event = models.ForeignKey(Event)

	status = models.CharField(max_length=20)
	remarks = models.TextField(blank=True)

	def __unicode__(self):
		return self.member.name + " → " + self.event.name