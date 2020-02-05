#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command
from wagtail import VERSION


def runtests():
    if not settings.configured:
        # Choose database for settings
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        }
        test_db = os.environ.get('DB', 'sqlite')
        if test_db == 'mysql':
            DATABASES['default'].update({
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'wagtail_modeltranslation',
                'USER': 'root',
            })
        elif test_db == 'postgres':
            DATABASES['default'].update({
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'wagtail_modeltranslation',
            })

        # Configure test environment
        import wagtail
        if VERSION < (2,):
            WAGTAIL_MODULES = [
                'wagtail.wagtailcore',
                'wagtail.wagtailadmin',
                'wagtail.wagtaildocs',
                'wagtail.wagtailsnippets',
                'wagtail.wagtailusers',
                'wagtail.wagtailimages',
                'wagtail.wagtailembeds',
                'wagtail.wagtailsearch',
                'wagtail.wagtailredirects',
                'wagtail.wagtailforms',
                'wagtail.wagtailsites',
                'wagtail.contrib.settings',
                'wagtail.contrib.wagtailapi',
            ]
            WAGTAIL_CORE = 'wagtail.wagtailcore'
        else:
            WAGTAIL_MODULES = [
                'wagtail.core',
                'wagtail.admin',
                'wagtail.documents',
                'wagtail.snippets',
                'wagtail.users',
                'wagtail.images',
                'wagtail.embeds',
                'wagtail.search',
                'wagtail.contrib.redirects',
                'wagtail.contrib.forms',
                'wagtail.sites',
                'wagtail.contrib.settings',
                'wagtail.api'
            ]
            WAGTAIL_CORE = 'wagtail.core'


        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'taggit',
                'rest_framework'] +
                WAGTAIL_MODULES + [
                'wagtail_modeltranslation.makemigrations',
                'wagtail_modeltranslation',
            ],
            # remove wagtailcore from serialization as translation columns have not been created at this point
            # (which causes OperationalError: no such column)
            TEST_NON_SERIALIZED_APPS=[WAGTAIL_CORE],
            ROOT_URLCONF=None,  # tests override urlconf, but it still needs to be defined
            LANGUAGES=(
                ('en', 'English'),
            ),
            MIDDLEWARE_CLASSES=(),
        )

    django.setup()
    failures = call_command(
        'test', 'wagtail_modeltranslation', interactive=False, failfast=False, verbosity=2)

    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
