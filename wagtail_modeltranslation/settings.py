# coding: utf-8
from django.conf import settings

from wagtail_modeltranslation.utils import import_from_string

# TODO: Consider making panel validation using class name to avoid the import_from_string method

# Load allowed CUSTOM_PANELS from Django settings
CUSTOM_SIMPLE_PANELS = [import_from_string(panel_class) for panel_class in
                        getattr(settings, 'WAGTAILMODELTRANSLATION_CUSTOM_SIMPLE_PANELS', [])]
CUSTOM_COMPOSED_PANELS = [import_from_string(panel_class) for panel_class in
                          getattr(settings, 'WAGTAILMODELTRANSLATION_CUSTOM_COMPOSED_PANELS', [])]

ORIGINAL_SLUG_LANGUAGE = getattr(settings, 'WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE', None)
