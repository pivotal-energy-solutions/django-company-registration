# -*- coding: utf-8 -*-
"""views.py: Django registration"""

from __future__ import unicode_literals

import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_change
from django.db.models import Q
from django import forms
from django.forms import HiddenInput
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from .forms import CompanyRegistrationForm, SetPasswordFormTOS
from .models import RegistrationProfile
from company_registration import get_site

from axis.core.decorators import permission_required_with_403
from axis.company.models import Company

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class Register(FormView):
    template_name = 'registration/registration_form.html'
    form_class = CompanyRegistrationForm

    @method_decorator(login_required)
    @method_decorator(permission_required_with_403('core.add_user'))
    def dispatch(self, *args, **kwargs):
        """Ensure we have access"""
        return super(Register, self).dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(Register, self).get_initial()
        initial['company'] = self.request.user.company
        return initial

    def get_form_kwargs(self):
        kwargs = super(Register, self).get_form_kwargs()
        comps = Company.objects.filter(is_customer=True, is_active=True)
        if not self.request.user.is_superuser:
            comps = Company.objects.filter_by_company(self.request.user.company, include_self=True)
            comps = comps.filter(
                Q(is_customer=False, is_active=True) | Q(id=self.request.user.company.id))
        kwargs['company_qs'] = comps
        return kwargs

    def get_form(self, form_class):
        form = super(Register, self).get_form(form_class)
        is_admin = self.request.user.is_superuser or self.request.user.is_company_admin
        if not is_admin:
            form.fields['is_company_admin'].widget = HiddenInput()
        return form

    def get_success_url(self, company=None, registration_sent=False):

        if registration_sent:
            return reverse("registration_complete")
        return reverse('company:view', kwargs={'type': company.company_type, 'pk': company.id})

    def form_valid(self, form):
        # activate user...
        site, request_site = get_site(self.request)

        form.cleaned_data['site'] = site
        form.cleaned_data['site_name'] = site.name
        form.cleaned_data['request_site'] = request_site
        form.cleaned_data['is_secure'] = self.request.is_secure()
        form.cleaned_data['requesting_user'] = self.request.user
        form.cleaned_data['request'] = self.request

        is_super = self.request.user.is_superuser
        is_allowed = form.cleaned_data['company'].id == self.request.user.company.id or is_super
        can_send = form.cleaned_data['company'].is_customer and form.cleaned_data['company'].is_active

        if not (is_allowed or can_send):
            form.cleaned_data['send_registration_email'] = False

        RegistrationProfile.objects.create_inactive_user(**form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url(
            form.cleaned_data.get('company'),
            form.cleaned_data.get('send_registration_email')))

class RegistrationComplete(TemplateView):
    template_name = 'registration/registration_complete.html'


class ActivationComplete(TemplateView):
    template_name = 'registration/activation_complete.html'


class Activate(TemplateView):
    template_name = 'registration/activation_failed.html'

    def get(self, request, *args, **kwargs):
        new_user = RegistrationProfile.objects.activate_user(kwargs['activation_key'], request)
        if new_user:
            # Log the user in and set their password
            new_user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, new_user)
            return HttpResponseRedirect(reverse('password_set'))
        return super(Activate, self).get(request, *args, **kwargs)


class PasswordSetTOS(FormView):
    """Class based set password and agree to TOS"""
    form_class = SetPasswordFormTOS
    token_generator = default_token_generator
    template_name = "registration/password_set_form.html"

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        """Ensure we have access"""
        return super(PasswordSetTOS, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """Save the password then give the user permissions"""
        form.save()
        messages.success(self.request, 'Your password has been set and permissions have been set!')
        return super(PasswordSetTOS, self).form_valid(form)

    def get_success_url(self):
        """Return them to update their profile"""
        profile = self.request.user.get_profile()
        return reverse('profile:detail', kwargs={'pk': profile.id})
