#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command


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
        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=(
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'taggit',
                'rest_framework',

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

                'wagtail_modeltranslation',
            ),
            # remove wagtailcore from serialization as translation columns have not been created at this point
            # (which causes OperationalError: no such column)
            TEST_NON_SERIALIZED_APPS=['wagtail.wagtailcore'],
            ROOT_URLCONF=None,  # tests override urlconf, but it still needs to be defined
            LANGUAGES=(
                ('en', 'English'),
            ),
            MIDDLEWARE_CLASSES=(),
            WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE='default',
        )

    if django.VERSION >= (1, 7):
        django.setup()
    failures = call_command(
        'test', 'wagtail_modeltranslation', interactive=False, failfast=False, verbosity=2)

    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
