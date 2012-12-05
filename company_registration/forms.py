# -*- coding: utf-8 -*-
"""forms.py: Django company_registration"""

import logging
from django import forms
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from passwords.fields import PasswordField
from apps.core.models import UserProfile
from django.utils.translation import ugettext_lazy as _

__author__ = 'Steven Klass'
__date__ = '4/3/12 9:01 PM'
__copyright__ = 'Copyright 2012 7Stalks Consulting. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

attrs_dict = {'class': 'required'}

# Registration
class AuthForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"), max_length=64,
                               widget=forms.TextInput(attrs={'size':32}))
#    password = PasswordField()
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'size':32}))

class RegistrationProfileForm(forms.ModelForm):

    username = forms.RegexField(regex=r'^[\w.@+-]+$', max_length=30,
                                widget=forms.TextInput(), label=_("Username"),
                                error_messages={'invalid': _("This value must contain only letters, numbers and underscores.")})
    first_name = forms.CharField(label="First Name",help_text='')
    last_name = forms.CharField(label="Last Name",help_text='')
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)))

    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name', 'email', 'title', 'work_phone',
                  'department', 'cell_phone', 'photo', 'is_public', 'rater_role', 'rater_id' )
        exclude= ('user', 'alt_companies', 'is_active', 'company')

    def __init__(self, *args, **kwargs):
        super(RegistrationProfileForm, self).__init__(*args, **kwargs)

        for key in ['username', 'email', 'first_name', 'last_name', 'work_phone', 'title']:
            self.fields[key].required = True

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """

        try:
            if User.objects.filter(email__iexact=self.cleaned_data['email']).count() > 1:
                raise forms.ValidationError(_("A user with that email address already exists."))
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
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'))

    def clean_tos(self):
        """
        Validate that the user accepted the Terms of Service.

        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(_(u'You must agree to the terms to register'))