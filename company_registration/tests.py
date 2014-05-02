# -*- coding: utf-8 -*-
"""tests.py: Django company_registration"""

from __future__ import unicode_literals

import re
import logging
import datetime

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core import mail
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from django.utils.importlib import import_module
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import _AuthUser
    get_user_model = lambda: _AuthUser

from apps.company.models import Company

from .admin import RegistrationAdmin
from .signals import user_activated, user_registered
from .managers import RegistrationManager
from .models import RegistrationProfile

__author__ = 'Steven Klass'
__date__ = '12/10/12 12:17 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

class CompanyRegistrationClient(Client):
    """This allows use to override the login.  Only to separate out the activate from the setting
     of the password"""

    def fake_login_user(self, username):
        """
        Sets the Factory to appear as if it has successfully logged into a site.

        Returns True if login is possible; False if the user is inactive,
         or if the sessions framework is not available.
        """
        user = get_user_model().objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        if user and user.is_active \
                and 'django.contrib.sessions' in settings.INSTALLED_APPS:
            engine = import_module(settings.SESSION_ENGINE)

            # Create a fake request to store login details.
            request = HttpRequest()
            if self.session:
                request.session = self.session
            else:
                request.session = engine.SessionStore()
            login(request, user)

            # Save the session values.
            request.session.save()

            # Set the cookie to represent the session.
            session_cookie = settings.SESSION_COOKIE_NAME
            self.cookies[session_cookie] = request.session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': settings.SESSION_COOKIE_DOMAIN,
                'secure': settings.SESSION_COOKIE_SECURE or None,
                'expires': None,
            }
            self.cookies[session_cookie].update(cookie_data)

            return True
        else:
            return False

    def get_host(self, site=None):
        return "127.0.0.1"

class CompanyRegistrationTests(TestCase):
    """Test the Company Registration."""
    client_class = CompanyRegistrationClient
    fixtures = ['test_geographic.json', 'test_companies_users.json']

    def setUp(self):
        """
        Create an instance of the default backend for use in testing,
        and set ``ACCOUNT_ACTIVATION_DAYS`` if it's not set already.

        """
        self.old_activation = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', None)
        if self.old_activation is None:
            settings.ACCOUNT_ACTIVATION_DAYS = 7 # pragma: no cover

    def tearDown(self):
        """
        Yank out ``ACCOUNT_ACTIVATION_DAYS`` back out if it wasn't
        originally set.

        """
        if self.old_activation is None:
            settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation # pragma: no cover

    def test_login_required(self):
        """You need to be logged in with perms to do this.."""
        url = reverse('registration_register')
        response = self.client.get(url)
        self.assertTrue(response.status_code, 302)

        redirect_url = re.search("(?P<url>https?://[^\s]+)", str(response)).group("url")
        self.assertTrue(url in redirect_url)
        self.assertTrue(reverse('login') in redirect_url)

    def test_registration(self):
        """
        Test the registration process: registration creates a new
        inactive account and a new profile with activation key,
        populates the correct account data and sends an activation
        email.

        """
        user = get_user_model().objects.get(id=1)
        self.client.login(username=user.username, password='pass')

        url = reverse('registration_register')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': user.company.id}

        response = self.client.post(url, data=data)
        # A registration profile was created, and an activation email was sent.
        self.assertRedirects(response, 'http://testserver%s' % reverse('registration_complete'))
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        new_user = RegistrationProfile.objects.all()[0].user

        # Details of the returned user must match what went in.
        self.assertEqual(new_user.first_name, data['first_name'])
        self.assertEqual(new_user.last_name, data['last_name'])
        self.assertEqual(new_user.email, data['email'])

        # New user must not be active.
        self.failIf(new_user.is_active)

        # Details of the returned user must match what went in.
        profile = new_user.get_profile()
        self.assertEqual(profile.company, user.company)
        self.assertEqual(profile.title, data['title'])
        self.assertEqual(profile.department, data['department'])
        self.assertEqual(profile.work_phone, data['work_phone'])
        self.assertEqual(profile.cell_phone, data['cell_phone'])
        self.assertEqual(profile.is_company_admin, False)
        self.assertEqual(profile.is_public, False)

        # Verify we got the success redirect url
        self.assertEqual(response.status_code, 302)
        new_url = re.search("(?P<url>https?://[^\s]+)", str(response)).group("url")
        self.assertTrue(reverse('registration_complete') in new_url)

    def test_valid_activation(self):
        """
        Test the activation process: activating within the permitted
        window sets the account's ``is_active`` field to ``True`` and
        resets the activation key.

        """
        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)

        url = reverse('registration_activate', kwargs={'activation_key': profile.activation_key})
        response = self.client.get(url)

        activated = get_user_model().objects.get(email=data['email'])
        self.assertEqual(activated.username, profile.user.username)
        self.failUnless(activated.is_active)

        # Fetch the profile again to verify its activation key has been reset.
        valid_profile = RegistrationProfile.objects.get(user=activated)
        self.assertEqual(valid_profile.activation_key, RegistrationProfile.ACTIVATED)

        self.assertEqual(response.status_code, 302)
        new_url = re.search("(?P<url>https?://[^\s]+)", str(response)).group("url")
        self.assertTrue(reverse('password_set') in new_url)

    def test_invalid_activation(self):
        """
        Test the activation process: trying to activate outside the
        permitted window fails, and leaves the account inactive.

        """
        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        expired_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=expired_user)

        exp = expired_user.date_joined - datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        expired_user.date_joined = exp
        expired_user.save()

        url = reverse('registration_activate', kwargs={'activation_key': profile.activation_key})
        response = self.client.get(url)

        self.failUnless(profile.activation_key_expired())
        self.assertFalse(expired_user.is_active)

        # Default template is a failure message.
        self.assertEqual(response.status_code, 200)

    def test_set_password_and_tos(self):
        """Validate you must agree to the TOS and that the passwords match"""

        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)
        active_user = RegistrationProfile.objects.activate_user(profile.activation_key)

        assert self.client.__class__ == CompanyRegistrationClient
        logged_in = self.client.fake_login_user(new_user.username)
        self.assertTrue(logged_in)

        data = {'new_password1': 'swordfish', 'new_password2': 'swordfish'}
        response = self.client.post(reverse('password_set'), data=data)
        self.assertFormError(response, 'form', field='tos', errors=['This field is required.'])

        data = {'new_password1': 'swordfish1', 'new_password2': 'swordfish', 'tos': 'checked'}
        response = self.client.post(reverse('password_set'), data=data)
        self.assertFormError(response, 'form', field='new_password2',
                             errors=['The two password fields didn\'t match.'])

        data = {'new_password1': 'swordfish', 'new_password2': 'swordfish', 'tos': 'checked'}
        response = self.client.post(reverse('password_set'), data=data)

        login_stat = self.client.login(username=new_user.username, password=data['new_password1'])
        self.assertTrue(login_stat)

        self.assertEqual(response.status_code, 302)
        new_url = re.search("(?P<url>https?://[^\s]+)", str(response)).group("url")
        self.assertTrue(reverse('profile:detail', kwargs={'pk': new_user.pk}) in new_url)

    def test_registration_signal(self):
        """
        Test that registering a user sends the ``user_registered``
        signal.

        """

        def receiver(sender, **kwargs):
            self.failUnless('user' in kwargs)
            self.assertEqual(kwargs['user'].first_name, 'Alice')
            self.failUnless('request' in kwargs)
            self.failUnless(isinstance(kwargs['request'], WSGIRequest))
            received_signals.append(kwargs.get('signal'))

        received_signals = []
        user_registered.connect(receiver, sender=RegistrationManager)

        user = get_user_model().objects.get(id=1)

        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': user.company.id}

        self.client.login(username=user.username, password='pass')
        self.client.post(reverse('registration_register'), data=data)

        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals, [user_registered])

    def test_activation_signal_success(self):
        """
        Test that successfully activating a user sends the
        ``user_activated`` signal.

        """
        def receiver(sender, **kwargs):
            self.failUnless('user' in kwargs)
            self.assertEqual(kwargs['user'].first_name, 'Alice')
            self.failUnless('request' in kwargs)
            self.failUnless(isinstance(kwargs['request'], WSGIRequest))
            received_signals.append(kwargs.get('signal'))

        received_signals = []
        user_activated.connect(receiver, sender=RegistrationManager)

        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)

        self.client.get(reverse('registration_activate',
                        kwargs={'activation_key': profile.activation_key}))

        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals, [user_activated])


    def test_activation_signal_failure(self):
        """
        Test that an unsuccessful activation attempt does not send the
        ``user_activated`` signal.

        """
        receiver = lambda sender, **kwargs: received_signals.append(kwargs.get('signal'))

        received_signals = []
        user_activated.connect(receiver, sender=RegistrationManager)

        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)

        new_user = get_user_model().objects.get(email=data['email'])
        new_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()

        self.client.get(reverse('registration_activate',
                        kwargs={'activation_key': profile.activation_key}))

        self.assertEqual(len(received_signals), 0)

    def test_email_send_action_no_sites(self):
        """
        Test re-sending of activation emails via admin action when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        Site._meta.installed = False
        admin_class = RegistrationAdmin(RegistrationProfile, admin.site)

        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)

        request = WSGIRequest({'HTTP_COOKIE': self.client.cookies, 'PATH_INFO': '/',
                               'QUERY_STRING': '', 'REMOTE_ADDR': '127.0.0.1',
                               'REQUEST_METHOD': 'GET', 'SCRIPT_NAME': '',
                               'SERVER_NAME': 'testserver', 'SERVER_PORT': '80',
                               'SERVER_PROTOCOL': 'HTTP/1.1', 'wsgi.version': (1,0),
                               'wsgi.url_scheme': 'http', 'wsgi.errors': self.client.errors,
                               'wsgi.multiprocess':True, 'wsgi.multithread': False,
                               'wsgi.run_once': False, 'wsgi.input': None,})
        request.user = new_user

        admin_class.resend_activation_email(request, RegistrationProfile.objects.all())
        self.assertEqual(len(mail.outbox), 2) # One on registering, one more on the resend.

        profile.activation_key = RegistrationProfile.ACTIVATED
        profile.save()

        admin_class.resend_activation_email(request, RegistrationProfile.objects.all())
        self.assertEqual(len(mail.outbox), 2) # No additional email because the account has activated.
        Site._meta.installed = True

    def test_activation_action(self):
        """
        Test manual activation of users view admin action.

        """
        admin_class = RegistrationAdmin(RegistrationProfile, admin.site)
        company = Company.objects.all()[0]
        data = {'first_name': 'Alice', 'last_name': 'LastName',
                'title': 'Title', 'work_phone': '123-456-7890',
                'department': 'department', 'cell_phone': '123-098-1234',
                'email': 'alice@example.com', 'company': company}
        new_user = RegistrationProfile.objects.create_inactive_user(**data)
        profile = RegistrationProfile.objects.get(user=new_user)

        admin_class.activate_users(WSGIRequest, RegistrationProfile.objects.all())
        self.failUnless(get_user_model().objects.get(email=data['email']).is_active)
