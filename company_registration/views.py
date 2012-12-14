# -*- coding: utf-8 -*-
"""views.py: Django registration"""

import logging
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from apps.generics.decorators import permission_required_with_403

from company_registration.models import RegistrationProfile
from company_registration import forms
from company_registration import get_site

from apps.company.models import Company

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class Register(FormView):
    template_name = 'registration/registration_form.html'
    form_class = forms.CompanyRegistrationForm

    @method_decorator(login_required)
    @method_decorator(permission_required_with_403('auth.add_user'))
    def dispatch(self, *args, **kwargs):
        """Ensure we have access"""
        return super(Register, self).dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(Register, self).get_initial()
        initial['company'] = self.request.user.company
        return initial

    def get_form_kwargs(self):
        kwargs = super(Register, self).get_form_kwargs()
        comps = Company.objects.filter_by_company(self.request.user.company, include_self=True)
        if not self.request.user.is_superuser:
            comps = comps.filter(Q(is_customer=False)|Q(id=self.request.user.company.id))
        kwargs['company_qs'] = comps
        return kwargs

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return reverse("registration_complete")

    def form_valid(self, form):
        # activate user...
        form.cleaned_data['site'] = get_site(self.request)
        form.cleaned_data['is_secure'] = self.request.is_secure()
        form.cleaned_data['requesting_user'] = self.request.user
        form.cleaned_data['request'] = self.request
        RegistrationProfile.objects.create_inactive_user(**form.cleaned_data)
        return super(Register, self).form_valid(form)

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


@login_required
def password_set(request, **kwargs):
    kwargs['template_name'] = "registration/password_set_form.html"
    kwargs['password_change_form'] = forms.SetPasswordFormTOS
    kwargs['post_change_redirect'] = reverse('profile_update')
    return password_change(request, **kwargs)