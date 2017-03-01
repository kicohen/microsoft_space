from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from msevents import views as msevents_views

urlpatterns = [
    url(r'^$', msevents_views.home, name='home'),
    url(r'^login$', auth_views.login, {'template_name':'socialnetwork/login.html'}, name='login'),
    url(r'^logout/$',auth_views.logout, {'next_page':'login'}, name='logout'),
]

