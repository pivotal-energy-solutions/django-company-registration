# -*- coding: utf-8 -*-"""signals.py: Django company_registration"""

import logging
from django.dispatch import Signal

__author__ = 'Steven Klass'
__date__ = '12/10/12 1:41 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


# A new user has registered.
user_registered = Signal(providing_args=["user", "request"])

# A user has activated his or her account.
user_activated = Signal(providing_args=["user", "request"])