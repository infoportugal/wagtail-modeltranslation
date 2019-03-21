#!/usr/bin/env python
import re

import os
from setuptools import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Please assure that the package version is defined as "__version__ = x.x.x" in ' + filename)


version = get_version("wagtail_modeltranslation", "__init__.py")

setup(
    name='wagtail-modeltranslation',
    version=version,
    description='Translates Wagtail CMS models using a registration approach.',
    long_description=(
        'The modeltranslation application can be used to translate dynamic '
        'content of existing models to an arbitrary number of languages '
        'without having to change the original model classes. It uses a '
        'registration approach (comparable to Django\'s admin app) to be able '
        'to add translations to existing or new projects and is fully '
        'integrated into the Wagtail admin backend.'),
    author='InfoPortugal, S.A.',
    author_email='suporte24@infoportugal.pt',
    maintainer='InfoPortugal, S.A.',
    maintainer_email='suporte24@infoportugal.pt',
    url='https://github.com/infoportugal/wagtail-modeltranslation',
    packages=[
        'wagtail_modeltranslation',
        'wagtail_modeltranslation.management',
        'wagtail_modeltranslation.management.commands',
        'wagtail_modeltranslation.templatetags',
        'wagtail_modeltranslation.makemigrations',
        'wagtail_modeltranslation.makemigrations.management',
        'wagtail_modeltranslation.makemigrations.management.commands',
        'wagtail_modeltranslation.migrate',
        'wagtail_modeltranslation.migrate.management',
        'wagtail_modeltranslation.migrate.management.commands'],
    package_data={'wagtail_modeltranslation': ['static/wagtail_modeltranslation/css/*.css',
                                               'static/wagtail_modeltranslation/js/*.js']},
    install_requires=['wagtail>=1.12', 'django-modeltranslation>=0.13'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'],
    license='New BSD')
