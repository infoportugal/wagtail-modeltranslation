from modeltranslation.management.commands.sync_translation_fields import Command as SyncTranslationsFieldsCommand
from modeltranslation.translator import translator
try:
    from wagtail.core.models import Page
except ImportError:
    from wagtail.wagtailcore.models import Page


old_get_registered_models = translator.get_registered_models

# Monkey patching, only return a model if it's Page
def get_page_model(self, abstract=True):
    models = old_get_registered_models(abstract)
    return [x for x in models if x is Page]


class Command(SyncTranslationsFieldsCommand):
    help = ("Detect new translatable fields or new available languages and"
            " sync Wagtail's Page database structure. Does not remove "
            " columns of removed languages or undeclared fields.")

    def handle(self, *args, **options):
        translator.get_registered_models = get_page_model.__get__(translator)

        try:
            super(Command, self).handle(*args, **options)

        finally:
            translator.get_registered_models = old_get_registered_models
