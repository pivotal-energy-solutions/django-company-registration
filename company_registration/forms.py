# -*- coding: utf-8 -*-
"""forms.py: Django company_registration"""

from __future__ import unicode_literals

import logging

from django import forms
from django.db.models import Q
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


__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class CompanyRegistrationForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.none())
    send_registration_email = forms.BooleanField(help_text=strings.SEND_REGISTRATION, required=False, initial=True)

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'title', 'work_phone', 'department',
                  'cell_phone', 'is_public', 'rater_role', 'rater_id', 'is_company_admin',
                  'company', 'send_registration_email')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        kwargs.setdefault('initial', {}).update({
            'company': self.user.company,
        })

        super(CompanyRegistrationForm, self).__init__(*args, **kwargs)

        self.setup_fields()

    def setup_fields(self):
        if self.user.is_superuser:
            company_qs = Company.objects.filter(is_active=True)
        else:
            is_active = Q(is_customer=False, is_active=True)
            is_self = Q(id=self.user.company.id)
            company_qs = Company.objects.filter_by_company(self.user.company, include_self=True) \
                                        .filter(is_active | is_self)

        self.fields['company'].queryset = company_qs

        # Setting help text and label here because UserProfile model is used in many places,
        # and the same help text does not apply in all those places.
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

        if not self.user.is_superuser and not self.user.is_company_admin:
            del self.fields['is_company_admin']


    def clean_email(self):
        """Validate that the email address is not already in use."""
        User = get_user_model()
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exists():
            raise forms.ValidationError(_("A user with that email address is not available"))
        return self.cleaned_data['email']

    def clean(self):
        """Validate that an user does not already exist for the same company."""
        cleaned_data = super(CompanyRegistrationForm, self).clean()
        User = get_user_model()

        first = cleaned_data['first_name']
        last = cleaned_data['last_name']
        comp = cleaned_data['company']
        count = User.objects.filter(first_name=first, last_name=last, company=comp).count()
        if count >= 1:
            raise forms.ValidationError(
                _("A user named {} {} already works for company {}".format(
                    first, last, company)))

        return cleaned_data


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

