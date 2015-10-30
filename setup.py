#!/usr/bin/env python
from distutils.core import setup


setup(
    name='wagtail-modeltranslation',
    version='0.3.1',
    description='Translates Wagtail CMS models using a registration approach.',
    long_description=(
        'The modeltranslation application can be used to translate dynamic '
        'content of existing models to an arbitrary number of languages '
        'without having to change the original model classes. It uses a '
        'registration approach (comparable to Django\'s admin app) to be able '
        'to add translations to existing or new projects and is fully '
        'integrated into the Wagtail admin backend.'),
    author='Rui Martins',
    author_email='rui.martins@infoportugal.pt',
    maintainer='Rui Martins',
    maintainer_email='rui.martins@infoportugal.pt',
    url='https://github.com/infoportugal/wagtail-modeltranslation',
    packages=[
        'wagtail_modeltranslation',
        'wagtail_modeltranslation.management',
        'wagtail_modeltranslation.management.commands',
        'wagtail_modeltranslation.templatetags'],
    package_data={'wagtail_modeltranslation': ['static/modeltranslation/css/*.css',
                                       'static/modeltranslation/js/*.js']},
    requires=['django(>=1.7)', 'wagtail(>=1.0)'],
    download_url='https://github.com/infoportugal/wagtail-modeltranslation/archive/v0.2.3.tar.gz',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'],
    license='New BSD')
