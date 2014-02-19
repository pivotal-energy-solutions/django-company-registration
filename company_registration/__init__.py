# -*- coding: utf-8 -*-
"""__init__.py: Django company_registration package container"""

__author__ = 'Steven Klass'
__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))
__date__ = '3/28/12 12:55 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]
__license__ = 'See the file LICENSE.txt for licensing information.'

from django.contrib.sites import models as site_models

def get_version():
    return __version__


def get_site(request):
    request_site = site_models.RequestSite(request)
    if site_models.Site._meta.installed:
        try:
            site = site_models.Site.objects.get(domain=request_site.domain)
        except site_models.Site.DoesNotExist:
            # No Site matches the actual domain we're on; site.name will probably be wrong.
            site = site_models.Site.objects.get_current()
    else:
        site = request_site
    return site, request_site
