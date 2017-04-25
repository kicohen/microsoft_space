from django.shortcuts import render, redirect, get_object_or_404, _get_queryset, get_list_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory

from django.contrib.auth.tokens import default_token_generator

from django.core import serializers
from django.core.mail import send_mail

from .models import *
from .forms import *

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from datetime import datetime

################################################################
#                         Static Pages                         #
################################################################

def home(request):
    context = createContext(request)
    return render(request, 'msevents/home.html', context)

def about(request):
    context = createContext(request)
    return render(request, 'msevents/about.html', context)

def spaces(request):
    context = createContext(request)
    return render(request, 'msevents/spaces.html', context)

################################################################
#                       Helper Functions                       #
################################################################

def createContext(request):
    if str(request.user) != 'AnonymousUser':
        logged_in = True
        account_type = request.user.profile.account_type
    else:
        logged_in = False
        account_type = "Guest"
    context = { 'account_type': account_type, 'logged_in':logged_in}
    return context

def clean_date(date):
    date=date.replace("-",'')

def fix_date(datetime):
    date = datetime[:datetime.find(' ')]
    date.replace("/",'-')
    time = datetime[datetime.find(' '):]
    hour = time[1:time.find(":")]
    minutes = time[4:6]
    am = time[-2:]
    if am == 'PM':
        hour = str(int(hour)+12)
    if int(minutes) < 10 and int(minutes) != 0:
        minutes = '0'+minutes
    if int(hour) < 10:
        hour = '0'+hour
    return(date+" "+hour+":"+minutes)

def combine(*args):
    new_list = []
    for arg in args:
        if type(arg) == list:
            new_list.extend(arg)
        else:
            new_list.append(arg)
    return new_list

def forms_are_valid(forms):
    for form in forms:
        if not form.is_valid():
            return False
    return True

def save_forms(forms):
    for form in forms:
        form.save()

def is_admin(request):
    if request.user.profile.account_type == 'AD':
        return True
    return False

def admin_only(request):
    context = createContext(request)
    context['message'] = "You do not have rights to view this page."
    return render(request, 'msevents/home.html', context)

def get_objects_or_404(klass, *args, **kwargs):
    """
    Get a set of filtered objects

    Uses filter() to return objects, or raise a Http404 exception if
    no objects matches.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    objects = queryset.filter(*args, **kwargs)
    if not objects:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
    return objects

################################################################
#                          User Pages                          #
################################################################

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
def members(request, message = ""):
    if not is_admin(request):
        return admin_only(request)

    objects = User.objects.all()
    context = createContext(request)
    context["message"] = message

    if objects.count() > 0:
        context['members'] = objects.order_by('username')
        return render(request, 'msevents/members.html', context)

@login_required
def edit_user(request):
    if not is_admin(request):
        return admin_only(request)

    user_id = request.GET.get('id', '')
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile
    context = createContext(request)
    context["user"] = user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if forms_are_valid([user_form, profile_form]):
            save_forms([user_form, profile_form])
            return members(request, "Successfully edited user " + user.first_name + " " + user.last_name)
    
    context['user_form'] = UserForm(instance=user)
    context['profile_form'] = ProfileForm(instance=profile)
    return render(request, 'msevents/user_edit.html', context)

################################################################
#                         Event Pages                          #
################################################################

def calendar(request):
    context = createContext(request)
    events = []
    for date in EventDate.objects.all():
        if date.event_id.status == 'CF' and date.event_id.open_to_public:
            event_data = dict()
            event_data['title'] = date.event_id.name
            event_data['startsAt'] = str(date.start_date)
            event_data['endsAt'] = str(date.end_date)
            event_data['color'] = {'primary':'#7FBA00', 'secondary':'#ddd'}
            event_data['link'] = "%s?id=%s" % (reverse("show_event"), str(date.event_id.pk))
            events.append(event_data)
    context['events'] = str(events)
    return render(request, 'msevents/calendar.html', context)

@login_required
def events(request):
    if not is_admin(request):
        return admin_only(request)
    event_dates = EventDate.objects.filter(start_date__gte=datetime.now())
    context = createContext(request)
    context['pastevents'] = False
    if event_dates.count() > 0:
        context['eventdates'] = event_dates.order_by('start_date')
        return render(request, 'msevents/events.html', context)
    context['message'] = "No events found."
    return render(request, 'msevents/events.html', context)

@login_required
def past_events(request):
    if not is_admin(request):
        return admin_only(request)
    event_dates = EventDate.objects.filter(start_date__lte=datetime.now())
    context = createContext(request)
    context['pastevents'] = True
    if event_dates.count() > 0:
        context['eventdates'] = event_dates.order_by('start_date')
        return render(request, 'msevents/events.html', context)
    context['message'] = "No events found."
    return render(request, 'msevents/events.html', context)

@login_required
@transaction.atomic
def request_event(request):
    context = createContext(request)
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_date_form = EventDateForm(request.POST)
        event_date_form.clean_date()
        if event_form.is_valid() and event_date_form.is_valid():
            event = event_form.save(commit=False)
            event.contact = request.user
            event.save()
            event_date = event_date_form.save(commit=False)
            event_date.event_id = event
            event_date.save()
            context['message']="Successfully requested event."
            return render(request, 'msevents/home.html', context)
        else: 
            print("error")
    else:
        event_form = EventForm()
        event_date_form = EventDateForm()
    context['event_form'] = event_form
    context['event_date_form'] = event_date_form
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
    # Get event
    eid = request.GET.get('id', '')
    event = get_object_or_404(Event, pk=eid)
    # Create base context
    context = createContext(request)
    context['event'] = event
    # If the form is being submitted, process the request and make the changes
    event_dates = EventDate.objects.filter(event_id=event)
    DateFormSet = modelformset_factory(EventDate, form=EventDateForm, extra=0)
    if request.method == 'POST':
        # Update the event model only
        if is_admin(request):
            event_form = EventAdminForm(request.POST, instance=event)
        else:
            event_form = EventForm(request.POST, instance=event)
        # Only update if the form is valid
        if event_form.is_valid():
            event_form.save()
        # Go through each of the event dates and locations
        formset = DateFormSet(request.POST, queryset=event_dates)
        for key in formset.data:
            if key[-4:] == 'date':
                formset.data[key] = fix_date(formset.data[key])

        new_dates = []
        if formset.is_valid():
            counter = 0
            for form in formset:
                form.is_valid()
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
                location_id = form.cleaned_data.get('location_id')
                if start_date and end_date and location_id:
                    new_dates.append(EventDate(start_date=start_date, end_date=end_date, location_id=location_id, event_id=event))

        try:
            with transaction.atomic():
                EventDate.objects.filter(event_id=event).delete()
                EventDate.objects.bulk_create(new_dates)
        except IntegrityError: #If the transaction failed
            # Error
            print("Error")
        context['message']="Successfully updated event."
        return render(request, 'msevents/home.html', context)
    # Create the forms to be displayed in the update view
    # The base event form
    if is_admin(request):
        event_form = EventAdminForm(instance=event)
    else:
        event_form = EventForm(instance=event)
    # Create the forms for the event date and locations
    formset = DateFormSet(queryset=event_dates)
    # Add the forms to the context
    context['event_form'] = event_form
    context['formset'] = formset
    # Render the request
    return render(request, 'msevents/event_update.html', context)

################################################################
#                       Location Pages                         #
################################################################

@login_required
def locations(request, message=""):
    if not is_admin(request):
        return admin_only(request)

    context = createContext(request)
    context['message'] = message
    context['locations'] = Location.objects.all()
    return render(request, 'msevents/locations.html', context)

@login_required
def location(request):
    if not is_admin(request):
        return admin_only(request)

    context = createContext(request)

    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return locations(request)
    
    context['form'] = LocationForm()
    return render(request, 'msevents/location.html', context)

@login_required
def edit_location(request):
    if not is_admin(request):
        return admin_only(request)

    location_id = request.GET.get('id', '')
    location = get_object_or_404(Location, pk=location_id)
    context = createContext(request)
    context['edit'] = True
    context['location'] = location

    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return locations(request, "Successfully edited location "+ location.room)
    
    context['form'] = LocationForm(instance=location)
    return render(request, 'msevents/location.html', context)

@login_required
def delete_location(request):
    location_id = request.GET.get('id', '')
    location = get_object_or_404(Location, pk=location_id)
    name = location.room
    location.delete()
    return locations(request, "Successfully deleted location "+name)
