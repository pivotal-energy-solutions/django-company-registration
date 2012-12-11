# -*- coding: utf-8 -*-
"""urls.py: Django """

import logging
from django.conf.urls import patterns, url
from company_registration import views, auth_urls

__author__ = 'Steven Klass'
__date__ = '4/3/12 8:59 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

registration_urls = patterns('',
    url(r'^register/$', views.Register.as_view(),
        name='registration_register'),
    url(r'^register/complete/$', views.RegistrationComplete.as_view(),
        name='registration_complete'),
    url(r'^activate/complete/$', views.ActivationComplete.as_view(),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', views.Activate.as_view(),
        name='registration_activate'),
    url(r'^password_set/$', views.password_set, name='password_set'),
)

urlpatterns = registration_urls + auth_urls.urlpatterns
