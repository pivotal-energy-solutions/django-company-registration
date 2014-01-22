# -*- coding: utf-8 -*-
"""forms.py: Django company_registration"""

from __future__ import unicode_literals

import logging

from django import forms
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User as _AuthUser
    get_user_model = lambda: _AuthUser

from passwords.fields import PasswordField

from apps.company.models import Company

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class CompanyRegistrationForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.none())
    twitter_id = forms.CharField(label="Twitter", help_text='', required=False)

    def __init__(self, *args, **kwargs):
        company_qs = kwargs.pop('company_qs', Company.objects.none())
        super(CompanyRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['company'].queryset = company_qs

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'title', 'work_phone', 'department',
                  'cell_phone', 'is_public', 'rater_role', 'rater_id', 'twitter_id',
                  'is_company_admin')
        exclude= ('user', 'username', 'alt_companies', 'is_active')

    def clean_email(self):
        """Validate that the email address is not already in use."""
        User = get_user_model()
        try:
            if User.objects.filter(email__iexact=self.cleaned_data['email']).count() >= 1:
                raise forms.ValidationError(_("A user with that email address is not available"))
        except User.DoesNotExist:
            pass
        return self.cleaned_data['email']


class SetPasswordFormTOS(SetPasswordForm):
    """
    Subclass of ``SetPasswordForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = PasswordField(label=_("New password"))
    new_password1 = PasswordField(label=_("New password confirmation"))
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_('I have read and agree to the Terms of Service'),
                             required=True)

    def clean_tos(self):
        """
        Validate that the user accepted the Terms of Service.

        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(_('You must agree to the terms to register'))

