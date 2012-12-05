# -*- coding: utf-8 -*-
"""views.py: Django registration"""

import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change
from django.http import Http404
from registration.views import register
from .forms import SetPasswordFormTOS

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

@login_required
def auth_register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None):
    """
        This a slight modification to the original to only allow user registration from company admins.
    """

    if not request.user.has_perm('user.add_user') and not request.user.profile.is_company_admin:
        messages.error(request, "You are not a company admin")
        error = "{} is not an admin and attempted to register a new user Group: {} Company Admin: {}"
        log.error(error.format(request.user , request.user.groups.all(), request.user.profile.is_company_admin))
        raise Http404

    return register(request, backend, success_url=success_url, form_class=form_class,
                    disallowed_url=disallowed_url, template_name=template_name,
                    extra_context=extra_context)

@login_required
def password_set(request, **kwargs):
    kwargs['template_name'] = "registration/password_set_form.html"
    kwargs['password_change_form'] = SetPasswordFormTOS
    return password_change(request, **kwargs)