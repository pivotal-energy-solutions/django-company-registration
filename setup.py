# -*- coding: utf-8 -*-
"""setup.py: Django django-company-registration"""

from distutils.core import setup
import os

# compile the list of packages available, because distutils doesn't have an easy way to do this
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('company_registration'):
    # ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        # strip 'company_registration/' or 'company_registration\'
        prefix = dirpath[21:]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(name='django-company-registration',
      version='1.0',
      description='This package is used in conjunction with django-registration to allow a '
                  'company to register new users rather than a self-subscribe model.',
      author='Steven Klass',
      author_email='sklass@pivotalenergysolutions.com',
      url='https://github.com/pivotal-energy-solutions/django-company-registration',
      package_dir={'company_registration': 'company_registration'},
      packages=packages,
      package_data={'company_registration': data_files},
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
)
