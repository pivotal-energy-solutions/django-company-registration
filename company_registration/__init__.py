# -*- coding: utf-8 -*-
"""__init__.py: Django company_registration package container"""

__name__ = 'company_registration'
__author__ = 'Pivotal Energy Solutions'
__version_info__ = (1, 0, "0rc1")
__version__ = '.'.join(map(str, __version_info__))
__date__ = '3/28/12 12:55 PM'
__copyright__ = 'Copyright 2012-2013 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]
__license__ = 'See the file LICENSE.txt for licensing information.'


def get_version():
    return __version__


def get_site(request):
    from django.contrib.sites import models as site_models
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
