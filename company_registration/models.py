# -*- coding: utf-8 -*-
"""models.py: Django registration"""

import logging
import datetime
from django.core.mail import EmailMultiAlternatives, mail_managers
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from managers import RegistrationManager


__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"
    activation_subject_template_name = "registration/activation_email_subject.txt"
    activation_text_template_name = "registration/activation_email.txt"
    activation_html_template_name = "registration/activation_email.html"

    user = models.ForeignKey(User, unique=True, related_name="registration_profiles")
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())

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
        requester = kwargs.get('requesting_user')
        mail_managers("New User {} from {} was Added".format(self.user, requester),
                      "Hey\n    {} just added {}\n\nBig Brother..".format(requester, self.user))



#class CustomRegistrationManager(registration.models.RegistrationManager):
#
#    def create_inactive_user(self, username, email, password, site, requester, company,
#                             send_email=True):
#        """
#        All we did was add in the requestor and the company.
#        """
#        new_user = User.objects.create_user(username, email, password)
#        new_user.is_active = False
#        new_user.save()
#
#        registration_profile = self.create_profile(new_user)
#
#        if send_email:
#            registration_profile.send_activation_email(site, requester, company)
#
#        return new_user
#
#    create_inactive_user = transaction.commit_on_success(create_inactive_user)
#
#class CustomRegistrationProfile(registration.models.RegistrationProfile):
#
#    objects = CustomRegistrationManager()
#
#    class Meta:
#        proxy = True
#
#    def send_activation_email(self, site, requester, company):
#        """
#            All we did was add in the requester and the company
#        """
#        ctx_dict = {'activation_key': self.activation_key,
#                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
#                    'site': site, 'user': self.user, 'admin': requester, 'company': company}
#        subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
#        subject = ''.join(subject.splitlines())
#        message = render_to_string('registration/activation_email.txt', ctx_dict)
#        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
#        mail_managers("New User {} from {} was Added".format(self.user, company),
#                      "Hey\n    {} just added {}\n\nBig Brother..".format(requester, self.user))
