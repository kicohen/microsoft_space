from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction

from django.contrib.auth.tokens import default_token_generator

from django.core import serializers
from django.core.mail import send_mail

from .models import Profile, Location, Event, EventDate, EventDateLocation, EventRole
from .forms import RegistrationForm, EventForm, EventDateForm, EventDateLocationForm

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from datetime import datetime
# Create your views here.

def createContext(request):
    if str(request.user) != 'AnonymousUser':
        logged_in = True
        account_type = request.user.profile.account_type
    else:
        logged_in = False
        account_type = "Guest"
    context = { 'account_type': account_type, 'logged_in':logged_in}
    return context

def home(request):
    context = createContext(request)
    return render(request, 'msevents/home.html', context)

def about(request):
    context = createContext(request)
    return render(request, 'msevents/about.html', context)

@login_required
def profile(request):
    context = createContext(request)
    events = Event.objects.filter(contact=request.user)
    context['events'] = events
    context['user'] = request.user
    return render(request, 'msevents/profile.html', context)

@login_required
def user(request):
    context = createContext(request)
    uid = request.GET.get('id', '')
    if uid == "":
        context['message'] = 'User not found'
        return render(request, 'msevents/home.html', context)
    else:
        context = createContext(request)
        user = get_object_or_404(User, pk=uid)
        events = Event.objects.filter(contact=user)
        context['events'] = events
        context['user'] = user
        return render(request, 'msevents/profile.html', context)

def spaces(request):
    context = createContext(request)
    return render(request, 'msevents/spaces.html', context)

def calendar(request):
    context = createContext(request)
    events = []
    for date in EventDate.objects.all():
        event_data = dict()
        event_data['title'] = date.event_id.name
        event_data['startsAt'] = str(date.start_date)
        event_data['endsAt'] = str(date.end_date)
        event_data['color'] = {'primary':'#7FBA00', 'secondary':'#ddd'}
        events.append(event_data)
    context['events'] = str(events)
    return render(request, 'msevents/calendar.html', context)

@transaction.atomic
def register(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'msevents/register.html', context)
    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'msevents/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'])
    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Welcome to the Microsoft Space at CMU.  Please click the link below to
verify your email address and complete the registration of your account:
  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))
    send_mail(subject="Verify Email Address",
              message= email_body,
              from_email="Microsoft Space <microsoft@cmu.edu>",
              recipient_list=[new_user.email])

    message = "A confirmation email has been sent to " + form.cleaned_data['email'] + ". Please click the link in that email to confirm your email address and complete your registration for your address book."
    context['message'] = message
    return render(request, 'msevents/home.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'msevents/home.html', {'message': "Thank you for confirming your email address. Please login to continue."})

@login_required
def members(request):
    if request.user.profile.account_type != 'AD':
        return render(request, 'msevents/home.html', {'message': "You do not have rights to view this page."})

    objects = User.objects.all()
    context = createContext(request)
    print(objects)
    if objects.count() > 0:
        context['members'] = objects.order_by('username')
        print('Here')
        return render(request, 'msevents/members.html', context)

@login_required
def events(request):
    if request.user.profile.account_type != 'AD':
        return render(request, 'msevents/home.html', {'message': "You do not have rights to view this page."})

    event_dates = EventDate.objects.all()
    context = createContext(request)
    if event_dates.count() > 0:
        context['eventdates'] = event_dates.order_by('start_date')
        return render(request, 'msevents/events.html', context)

def clean_date(date):
    date=date.replace("-",'')

@login_required
@transaction.atomic
def request_event(request):
    context = createContext(request)
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_date_form = EventDateForm(request.POST)
        event_location_form = EventDateLocationForm(request.POST)
        event_date_form.clean_date()
        if event_form.is_valid() and event_date_form.is_valid() and event_location_form.is_valid():
            event = event_form.save(commit=False)
            event.contact = request.user
            event.save()
            event_date = event_date_form.save(commit=False)
            event_date.event_id = event
            event_date.save()
            event_location = event_location_form.save(commit=False)
            event_location.eventdate_id = event_date
            event_location.save()
            context['message']="Successfully requsted event."
            return render(request, 'msevents/calendar.html', context)
        else: 
            print("error")
    else:
        event_form = EventForm()
        event_date_form = EventDateForm()
        event_location_form = EventDateLocationForm()
    context['event_form'] = event_form
    context['event_date_form'] = event_date_form
    context['event_location_form'] = event_location_form
    return render(request, 'msevents/request_event.html', context)

def show_event(request):
    eid = request.GET.get('id', '')
    event = get_object_or_404(Event, pk=eid)
    context = createContext(request)
    context['event'] = event
    context['event_dates'] = EventDate.objects.filter(event_id=event)
    return render(request, 'msevents/event_details.html', context)

@login_required
def edit_event(request):
    eid = request.GET.get('id', '')
    event = get_object_or_404(Event, pk=eid)
    context = createContext(request)
    context['event'] = event
    return render(request, 'msevents/request_event.html', context)
