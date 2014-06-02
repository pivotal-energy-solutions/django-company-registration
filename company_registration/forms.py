# -*- coding: utf-8 -*-
"""forms.py: Django company_registration"""

from __future__ import unicode_literals

import logging

from django import forms
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User as _AuthUser
    get_user_model = lambda: _AuthUser

from passwords.fields import PasswordField

from apps.company.models import Company
from . import strings

# TODO: REMOVE ME
IS_LEGACY = settings.AUTH_USER_MODEL == 'auth.User'

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class CompanyRegistrationForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.none())
    twitter_id = forms.CharField(label="Twitter", help_text='', required=False)

    if IS_LEGACY:
        email = forms.EmailField(widget=forms.TextInput(), required=True)
        first_name = forms.CharField(label="First Name",help_text='', required=True)
        last_name = forms.CharField(label="Last Name",help_text='', required=True)

    def __init__(self, *args, **kwargs):
        company_qs = kwargs.pop('company_qs', Company.objects.none())
        super(CompanyRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['company'].queryset = company_qs

        # Setting help text and label here because UserProfile model is used in many places,
        #  and the same help text does not apply in all those places.
        self.fields['company'].help_text = strings.COMPANY_REGISTRATION_FORM_COMPANY
        self.fields['first_name'].help_text = strings.COMPANY_REGISTRATION_FORM_FIRST_NAME
        self.fields['last_name'].help_text = strings.COMPANY_REGISTRATION_FORM_LAST_NAME
        self.fields['email'].help_text = strings.COMPANY_REGISTRATION_FORM_EMAIL
        self.fields['work_phone'].help_text = strings.COMPANY_REGISTRATION_FORM_WORK_PHONE
        self.fields['cell_phone'].help_text = strings.COMPANY_REGISTRATION_FORM_CELL_PHONE
        self.fields['title'].help_text = strings.COMPANY_REGISTRATION_FORM_TITLE
        self.fields['department'].help_text = strings.COMPANY_REGISTRATION_FORM_DEPARTMENT
        self.fields['rater_role'].help_text = strings.COMPANY_REGISTRATION_FORM_RATER_ROLE
        self.fields['rater_id'].help_text = strings.COMPANY_REGISTRATION_FORM_RATER_ID
        self.fields['is_company_admin'].help_text = strings.COMPANY_REGISTRATION_FORM_IS_COMPANY_ADMIN

        self.fields['company'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_COMPANY
        self.fields['email'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_EMAIL
        self.fields['work_phone'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_WORK_PHONE
        self.fields['cell_phone'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_CELL_PHONE
        self.fields['rater_id'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_RATER_ID
        self.fields['is_company_admin'].label = strings.COMPANY_REGISTRATION_FORM_VERBOSE_NAME_IS_COMPANY_ADMIN


    class Meta:
        if IS_LEGACY:
            from apps.core.models import UserProfile
            model = UserProfile
        else:
            model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'title', 'work_phone', 'department',
                  'cell_phone', 'is_public', 'rater_role', 'rater_id', 'twitter_id',
                  'is_company_admin')
        if IS_LEGACY:
            fields += ('photo',)
        exclude= ('user', 'username', 'alt_companies', 'is_active')


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

