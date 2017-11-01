# -*- coding: utf-8 -*-
"""tasks.py: Django company_registration"""

from __future__ import unicode_literals

import logging

from celery import shared_task
from company_registration.models import RegistrationProfile
from django.conf import settings


__author__ = 'Steven Klass'
__date__ = '1/9/13 2:56 PM'
__copyright__ = 'Copyright 2012 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

@shared_task
def clear_expired_registrations(**kwargs):
    """
    Crontab to clear expired registrations
    :param kwargs: Not Unsed
    """
    kwargs['loglevel'] = logging.DEBUG if getattr(settings, 'DEBUG', False) else logging.ERROR
    return RegistrationProfile.objects.delete_expired_users()
