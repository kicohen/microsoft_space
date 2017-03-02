from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	EVENT_ORGANIZER = 'EO'
	GATE_KEEPER = 'GK'
	ADMIN = "AD"

	ACCOUNT_TYPES = (
		(EVENT_ORGANIZER, 'Event Organizer'),
		(GATE_KEEPER, 'Gate Keeper'),
		(ADMIN, 'Administrator')
	)
	account_type = models.CharField(
        max_length=2,
        choices=ACCOUNT_TYPES,
        default=EVENT_ORGANIZER,
    )

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance)

	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		instance.profile.save()

class Location(models.Model):
	building = models.CharField(max_length=160, default="Microsoft Space")
	room = models.CharField(max_length=160)
	details = models.TextField(max_length=600, blank=True)

class Event(models.Model):
	name = models.CharField(max_length=160)
	organization = models.CharField(max_length=160)

	INITIAL_REQUEST = 'IR'
	EVENT_CONFIRMED = 'CF'
	EVENT_COMPLETED = 'EC'
	EVENT_CANCELLED = 'EX'
	EVENT_DECLINED = 'ED'
	
	EVENT_STATUS_TYPES = (
		(INITIAL_REQUEST, 'Initial Request'),
		(EVENT_CONFIRMED, 'Event Confirmed'),
		(EVENT_DECLINED, 'Event Declined'),
		(EVENT_CANCELLED, 'Event Canceled'),
		(EVENT_COMPLETED, 'Event Completed')
	)

	status = models.CharField(
        max_length=2,
        choices=EVENT_STATUS_TYPES,
        default=INITIAL_REQUEST,
    )
	contact = models.ForeignKey(User)
	head_count = models.IntegerField(blank=True)
	open_to_public = models.BooleanField()
	notes = models.TextField(max_length=1000, blank=True)

class EventDate(models.Model):
	event_id = models.ForeignKey(Event)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()

class EventDateLocation(models.Model):
	eventdate_id = models.ForeignKey(EventDate)
	location_id = models.ForeignKey(Location)

class EventRole(models.Model):
	user_id = models.ForeignKey(User, blank=True, null=True)
	event_id = models.ForeignKey(Event)
	name = models.CharField(max_length=160)