# coding: utf-8
from django.apps import AppConfig


class ModeltranslationConfig(AppConfig):
    name = 'wagtail_modeltranslation'
    verbose_name = 'Wagtail Modeltranslation'

    def ready(self):
        from django.conf import settings
        # Add Wagtail defined fields as modeltranslation custom fields
        setattr(settings, 'MODELTRANSLATION_CUSTOM_FIELDS', getattr(settings, 'MODELTRANSLATION_CUSTOM_FIELDS', ()) + (
            'StreamField', 'RichTextField'))

        from modeltranslation.models import handle_translation_registrations
        handle_translation_registrations()

        from patch_wagtailadmin import patch_wagtail_models
        patch_wagtail_models()
