#!/usr/bin/env python
from distutils.core import setup

setup(
    name='wagtail-modeltranslation',
    version='0.8.0-alpha',
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
        'wagtail_modeltranslation.makemigrations.management.commands'],
    package_data={'wagtail_modeltranslation': ['static/wagtail_modeltranslation/css/*.css',
                                               'static/wagtail_modeltranslation/js/*.js']},
    install_requires=['wagtail(>=1.4)', 'django-modeltranslation(>0.12.1)'],
    dependency_links=[
        "http://github.com/deschler/django-modeltranslation/tarball/00fc7f1804aaa1b1e37af48e67871080851e14b0#egg=django-modeltranslation-0.12.2"
    ],
    download_url='https://github.com/infoportugal/wagtail-modeltranslation/archive/v0.6rc2.tar.gz',
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
