# coding: utf-8

from django.core.management.base import BaseCommand
from modeltranslation import settings as mt_settings
from modeltranslation.utils import build_localized_fieldname
from wagtail.wagtailcore.models import Page
from wagtail_modeltranslation.contextlib import use_language


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        update_fields = ['url_path']
        for language in mt_settings.AVAILABLE_LANGUAGES:
            localized_url_path = build_localized_fieldname('url_path', language)
            update_fields.append(localized_url_path)
        self.update_fields = update_fields

    def set_subtree(self, root, parent):
        root.set_url_path(parent)
        root.save(update_fields=self.update_fields)
        for child in root.get_children():
            self.set_subtree(child, root)

    def handle(self, **options):
        with use_language(mt_settings.DEFAULT_LANGUAGE):
            for node in Page.get_root_nodes():
                self.set_subtree(node, None)
