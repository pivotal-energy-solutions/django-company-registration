# -*- coding: utf-8 -*-
"""tasks.py: Django company_registration"""

import logging
from celery.schedules import crontab
from celery.task.base import periodic_task
from company_registration.models import RegistrationProfile
import settings


__author__ = 'Steven Klass'
__date__ = '1/9/13 2:56 PM'
__copyright__ = 'Copyright 2012 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

@periodic_task(run_every=crontab(hour="2", minute="20", day_of_week="*"))
def clear_expired_registrations(**kwargs):
    """
    Crontab to clear expired registrations
    :param kwargs: Not Unsed
    """
    kwargs['log'] = clear_expired_registrations.get_logger()
    kwargs['loglevel'] = logging.DEBUG if settings.DEBUG else logging.ERROR
    return RegistrationProfile.objects.delete_expired_users()