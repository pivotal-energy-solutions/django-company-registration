# -*- coding: utf-8 -*-
"""models.py: Django registration"""

import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import mail_managers
from django.db import transaction
from django.template.loader import render_to_string
import registration

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

class CustomRegistrationManager(registration.models.RegistrationManager):

    def create_inactive_user(self, username, email, password, site, requester, company,
                             send_email=True):
        """
        All we did was add in the requestor and the company.
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site, requester, company)

        return new_user

    create_inactive_user = transaction.commit_on_success(create_inactive_user)

class CustomRegistrationProfile(registration.models.RegistrationProfile):

    objects = CustomRegistrationManager()

    class Meta:
        proxy = True

    def send_activation_email(self, site, requester, company):
        """
            All we did was add in the requester and the company
        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site, 'user': self.user, 'admin': requester, 'company': company}
        subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
        subject = ''.join(subject.splitlines())
        message = render_to_string('registration/activation_email.txt', ctx_dict)
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        mail_managers("New User {} from {} was Added".format(self.user, company),
                      "Hey\n    {} just added {}\n\nBig Brother..".format(requester, self.user))
