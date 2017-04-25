from django import forms

from django.contrib.auth.models import User
from .models import *
from django.utils.translation import ugettext_lazy as _

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ()

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = (
            'status',
            'contact',
        )

class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = (
            'contact',
        )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('account_type',)

def fix_date(datetime):
    print(datetime)
    date = datetime[:datetime.find(' ')]
    date.replace("/",'-')
    time = datetime[datetime.find(' '):]
    hour = time[1:time.find(":")]
    minutes = time[4:6]
    am = time[-2:]
    if am == 'PM':
        hour = str(int(hour)+12)
    if int(minutes) < 10:
        minutes = '0'+minutes
    if int(hour) < 10:
        hour = '0'+hour
    print(date+hour+minutes)
    return(date+" "+hour+":"+minutes)

class CustomLocationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()

class EventDateForm(forms.ModelForm):
    class Meta:
        model = EventDate
        exclude = ('event_id',)

    def clean_date(self):
        start_date = self.data['start_date']
        end_date = self.data['end_date']
        self.data['start_date'] = fix_date(start_date)
        print(self.data['start_date'])
        self.data['end_date'] = fix_date(end_date)
        return self.data

class EventDateLocationForm(forms.ModelForm):
    location_id = CustomLocationChoiceField(queryset=Location.objects.all(), label="Location")

    class Meta:
        model = EventDateLocation
        exclude = ('event_id','eventdate_id')