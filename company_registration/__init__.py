# -*- coding: utf-8 -*-
"""__init__.py: Django company_registration package container"""

__name__ = 'company_registration'
__author__ = 'Pivotal Energy Solutions'
__version_info__ = (1, 1, 4)
__version__ = '.'.join(map(str, __version_info__))
__date__ = '3/28/12 12:55 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]
__license__ = 'See the file LICENSE.txt for licensing information.'


def get_version():
    return __version__
