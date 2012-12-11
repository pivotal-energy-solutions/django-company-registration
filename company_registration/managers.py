# -*- coding: utf-8 -*-
"""managers.py: Django company_registration"""

import logging
import string
import random
from hashlib import sha1
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import signals


__author__ = 'Steven Klass'
__date__ = '12/10/12 1:38 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class RegistrationManager(models.Manager):
    """Provides shortcuts to account creation and activation"""

    def create_inactive_user(self, **kwargs):

        new_user = self._get_new_inactive_user(**kwargs)
        registration_profile = self._create_registration_profile(new_user)
        kwargs['user'] = new_user
        if kwargs.get('send_email', True) and new_user.userprofile.company.is_active:
            registration_profile.send_activation_email(**kwargs)
        return new_user

    def activate_user(self, activation_key):
        """returns user object if successful, otherwise returns false"""
        try:
            profile = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return False
        if not profile.activation_key_expired():
            user = profile.user
            user.is_active = True
            user.save()
            profile.activation_key = self.model.ACTIVATED
            profile.save()
            return user
        return False

    def delete_expired_users(self):
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()

    def _get_new_inactive_user(self, **kwargs):
        """Create a new inactive user with a profile"""
        username = slugify(kwargs.get('email').split("@", 1)[0][:25])
        users = User.objects.filter(username=username).count()
        if users > 0:
            username += str(users + 1)
        new_user, create = User.objects.get_or_create(
            email=kwargs.get('email'),
            defaults=dict(username=username, is_active=False,
                          first_name=kwargs.get('first_name'), last_name=kwargs.get('last_name')))
        new_user.set_unusable_password()
        new_user.groups.add(kwargs.get('company').group)
        new_user.save()

        signals.user_registered.send(sender=self.__class__)

        profile = new_user.get_profile()
        profile.company = kwargs.get('company')
        for key, value in kwargs.items():
            if key in ['email', 'first_name', 'last_name']:
                continue
            setattr(profile, key, value)
        profile.save()
        return new_user

    def _create_registration_profile(self, user):
        salt = sha1(str(random.random())).hexdigest()[:5]
        activation_key = sha1(salt + user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)
