# -*- coding: utf-8 -*-
"""urls.py: Django """

import logging
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from views import auth_register, password_set
from forms import RegistrationProfileForm
from .forms import AuthForm
from registration.views import activate

__author__ = 'Steven Klass'
__date__ = '4/3/12 8:59 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

urlpatterns = patterns('',
    url(r'^login/$', login, {'authentication_form': AuthForm}, name="login"),
    url(r'^logout/$', logout, {'next_page': '/',}, name='logout'),
#    url(r'^', include('django.contrib.auth.urls')),
    url(r'^register/$', auth_register,
            {'backend': 'company_registration.backends.RegistrationBackend',
             'form_class':RegistrationProfileForm }, name="registration_register"),
    url(r'^activate/(?P<activation_key>\w+)/$', activate,
            {'backend': 'company_registration.backends.RegistrationBackend'}),
    url(r'password_set/$', password_set, name='password_set'),
    url(r'^', include('registration.backends.default.urls')),
)