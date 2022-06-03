#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

import django
from django.core.management import execute_from_command_line
from django.core.management import call_command

os.environ['DJANGO_SETTINGS_MODULE'] = 'wagtail_modeltranslation.tests.settings'


def migrate():
    django.setup()
    call_command('makemigrations', 'tests', verbosity=2, interactive=False)


def runtests():
    argv = [sys.argv[0], 'test', 'wagtail_modeltranslation']
    execute_from_command_line(argv)


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if 'migrate' in args:
        migrate()
    else:
        runtests()
