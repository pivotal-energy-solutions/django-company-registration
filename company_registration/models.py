# -*- coding: utf-8 -*-
"""models.py: Django registration"""

from __future__ import unicode_literals

import logging
import datetime
from dateutil.tz import tzlocal
from django.core.mail import EmailMultiAlternatives, mail_managers
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
import sys
from managers import RegistrationManager


__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class RegistrationProfile(models.Model):
    ACTIVATED = "ALREADY_ACTIVATED"
    activation_subject_template_name = "registration/activation_email_subject.txt"
    activation_text_template_name = "registration/activation_email.txt"
    activation_html_template_name = "registration/activation_email.html"

    user = models.ForeignKey(User, unique=True, related_name="registration_profiles")
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return "Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        summed_date = self.user.date_joined + expiration_date
        return self.activation_key == self.ACTIVATED or \
               (summed_date <= datetime.datetime.now(tzlocal()))

    def send_activation_email(self, **kwargs):

        kwargs['activation_key'] = self.activation_key
        kwargs['expiration_days'] = settings.ACCOUNT_ACTIVATION_DAYS
        subject = render_to_string(self.activation_subject_template_name, kwargs).splitlines()
        subject = "".join(subject)

        text_message = render_to_string(self.activation_text_template_name, kwargs)
        html_message = render_to_string(self.activation_html_template_name, kwargs)

        msg = EmailMultiAlternatives(subject, text_message, settings.DEFAULT_FROM_EMAIL,[self.user.email])
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        # Let administrators know..
        if 'test' not in sys.argv:
            requester = kwargs.get('requesting_user')
            mail_managers("New User {} from {} was Added".format(self.user, requester),
                          "Hey\n    {} just added {}\n\nBig Brother..".format(requester, self.user))
