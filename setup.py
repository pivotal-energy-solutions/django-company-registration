# -*- coding: utf-8 -*-
"""setup.py: Django django-company-registration"""

from distutils.core import setup

setup(name='django-company-registration',
      version='1.0',
      description='This package is used in conjunction with django-registration to allow a '
                  'company to register new users rather than a self-subscribe model.',
      author='Steven Klass',
      author_email='sklass@pivotalenergysolutions.com',
      url='https://github.com/pivotal-energy-solutions/django-company-registration',
      license='lgpl',
      classifiers=[
           'Development Status :: 2 - Pre-Alpha',
           'Environment :: Web Environment',
           'Framework :: Django',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
           'Operating System :: OS Independent',
           'Programming Language :: Python',
           'Topic :: Software Development',
      ],
      packages=['company_registration'],
      requires=['django (>=1.2)',],
)
