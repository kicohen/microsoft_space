from django.contrib import admin

# Register your models here.
from .models import Profile, Location, Event, EventDate, EventRole

admin.site.register(Profile)
admin.site.register(Location)
admin.site.register(Event)
admin.site.register(EventDate)
admin.site.register(EventRole)