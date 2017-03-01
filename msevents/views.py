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
from .forms import RegistrationForm

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

def profile(request):
	context = createContext(request)
	return render(request, 'msevents/home.html', context)

def spaces(request):
	context = createContext(request)
	return render(request, 'msevents/spaces.html', context)

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

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="Microsoft@cmu.edu",
              recipient_list=[new_user.email])

    message = "A confirmation email has been sent to" + form.cleaned_data['email'] + ". Please click the link in that email to confirm your email address and complete your registration for your address book."
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



