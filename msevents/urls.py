from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from msevents import views as msevents_views

urlpatterns = [
    url(r'^$', msevents_views.home, name='home'),
    url(r'^spaces$', msevents_views.spaces, name='spaces'),
    url(r'^profile$', msevents_views.profile, name='profile'),
    url(r'^calendar$', msevents_views.calendar, name='calendar'),
    url(r'^events$', msevents_views.events, name='events'),
    url(r'^request_event$', msevents_views.request_event, name='request_event'),
    url(r'^login$', auth_views.login, {'template_name':'msevents/login.html'}, name='login'),
    url(r'^logout/$',auth_views.logout, {'next_page':'home'}, name='logout'),
    url(r'^register$', msevents_views.register, name='register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$',
        msevents_views.confirm_registration, name='confirm'),
]