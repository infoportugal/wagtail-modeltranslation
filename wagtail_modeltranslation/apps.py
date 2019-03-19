# coding: utf-8
from __future__ import absolute_import

from django.apps import AppConfig


class ModeltranslationConfig(AppConfig):
    name = 'wagtail_modeltranslation'
    verbose_name = 'Wagtail Modeltranslation'

    def ready(self):
        from django.conf import settings
        from modeltranslation import settings as mt_settings

        # Add Wagtail defined fields as modeltranslation custom fields
        wagtail_fields = (
            'StreamField',
            'RichTextField',
        )

        # update both the standard settings and the modeltranslation settings,
        # as we cannot guarantee the load order, and so django_modeltranslation
        # may bootstrap itself either before, or after, our ready() gets called.
        custom_fields = getattr(settings, 'MODELTRANSLATION_CUSTOM_FIELDS', list())
        setattr(settings, 'MODELTRANSLATION_CUSTOM_FIELDS', list(set(custom_fields + wagtail_fields)))

        mt_custom_fields = getattr(mt_settings, 'CUSTOM_FIELDS', list())
        setattr(mt_settings, 'CUSTOM_FIELDS', list(set(mt_custom_fields + wagtail_fields)))

        from modeltranslation.models import handle_translation_registrations
        handle_translation_registrations()

        from .patch_wagtailadmin import patch_wagtail_models
        patch_wagtail_models()
