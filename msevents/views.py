from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction

from django.core import serializers

from .models import Profile, Location, Event, EventDate, EventDateLocation, EventRole

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from datetime import datetime
# Create your views here.

def home(request):
	pass
	