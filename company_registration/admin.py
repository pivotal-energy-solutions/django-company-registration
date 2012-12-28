# -*- coding: utf-8 -*-"""admin.py: Django company_registration"""

import logging
from django.contrib import admin
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from models import RegistrationProfile

__author__ = 'Steven Klass'
__date__ = '12/11/12 10:48 AM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email']
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ['user']
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def activate_users(self, request, queryset):
        """
        Activates the selected users, if they are not alrady
        activated.

        """
        for profile in queryset:
            RegistrationProfile.objects.activate_user(profile.activation_key)
    activate_users.short_description = _("Activate users")

    def resend_activation_email(self, request, queryset, get_site=None):
        """
        Re-sends activation emails for the selected users.

        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.

        """
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        for profile in queryset:
            if not profile.activation_key_expired():
                kwargs = {}
                kwargs['site'] = site
                kwargs['is_secure'] = request.is_secure()
                kwargs['requesting_user'] = request.user
                kwargs['request'] = request
                profile.send_activation_email(**kwargs)
    resend_activation_email.short_description = _("Re-send activation emails")

admin.site.register(RegistrationProfile, RegistrationAdmin)