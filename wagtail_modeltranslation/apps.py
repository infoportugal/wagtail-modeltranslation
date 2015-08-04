# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ModeltranslationConfig(AppConfig):
    name = 'wagtail_modeltranslation'
    verbose_name = 'Wagtail Modeltranslation'

    def ready(self):
        from wagtail_modeltranslation.models import handle_translation_registrations
        handle_translation_registrations()
