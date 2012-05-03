from django.core.management.base import BaseCommand, CommandError
from openduty.models import *
from datetime import timedelta
from django.utils import timezone
from django.template.loader import render_to_string

class Command(BaseCommand):
	args = '<alert_time>'
	help = "Sends reminders <alert_time> hour(s) prior to event"

	def handle(self, *args, **options):
		try:
			alert_time = int(args[0])
			alert_range = timezone.now() + timedelta(hours=alert_time)

			for event in Event.objects.filter(reminder_sent=False, begin__lte=alert_range):
				for member in event.assignments.all():
					member.user.email_user("OpenDuty: Event Reminder ("+event.name+")", render_to_string("event/reminder_email.html", {'event': event}))
				event.reminder_sent = True
				event.save()

			self.stdout.write("Successfully sent reminders\n")
		except IndexError:
			raise CommandError("<alert_time> not present")
