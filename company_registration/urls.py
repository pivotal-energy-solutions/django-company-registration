# -*- coding: utf-8 -*-
"""urls.py: Django """

from __future__ import unicode_literals

import logging
from django.conf.urls import url
from company_registration import views


__author__ = 'Steven Klass'
__date__ = '4/3/12 8:59 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

urlpatterns = [
    url(r'^register/$', views.Register.as_view(),
        name='registration_register'),
    url(r'^register/complete/$', views.RegistrationComplete.as_view(),
        name='registration_complete'),
    url(r'^activated/complete/$', views.ActivationComplete.as_view(),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', views.Activate.as_view(),
        name='registration_activate'),
    url(r'^password_set/$', views.PasswordSetTOS.as_view(), name='password_set'),
]
