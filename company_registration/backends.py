# -*- coding: utf-8 -*-
"""backends.py: Django registration"""

import logging
from django.core import urlresolvers
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import RequestSite, Site
from registration import signals
from registration.backends.default import DefaultBackend
from apps.core.models import UserProfile
from .models import CustomRegistrationProfile
from .views import password_set

__author__ = 'Steven Klass'
__date__ = '10/4/11 4:30 PM'
__copyright__ = 'Copyright 2011 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass']

log = logging.getLogger(__name__)

class RegistrationBackend(DefaultBackend):
    """This sets a slightly different workflow.  Company administrators will create accounts for users.
       Once the end user gets an email and clicks the link he/she will become active and set themselves
       a password
    """
    def register(self, request, **kwargs):
        """We simply add on the profile information for the user creation"""

        username, email, = kwargs['username'], kwargs['email'],
        password = username

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        new_user = CustomRegistrationProfile.objects.create_inactive_user(username, email,
                                                                          password, site,
                                                                          request.user,
                                                                          request.user.company)
        signals.user_registered.send(sender=self.__class__, user=new_user, request=request)

        new_user.last_name = kwargs['last_name']
        new_user.first_name = kwargs['first_name']
        new_user.save()

        profile = UserProfile.objects.get(user=new_user)
        if request.user.company:
            profile.company = request.user.company
        for key,value in kwargs.items():
            if key in ['username', 'email', 'first_name','last_name']:continue
            setattr(profile, key, value)
        profile.save()
        new_user.save()
        return new_user

    def post_activation_redirect(self, request, user):
        """
        We need them to change their password to something they know..
        """
        new_user = authenticate(username=user.username, password=user.username)
        login(request, new_user)
        return urlresolvers.reverse(password_set), (), {}
