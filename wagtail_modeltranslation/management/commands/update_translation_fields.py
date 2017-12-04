# coding: utf-8

from django.core.management.base import BaseCommand
from django.db.models import F, Q
from modeltranslation.settings import DEFAULT_LANGUAGE
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname
from wagtail.wagtailcore.models import Page


class Command(BaseCommand):
    help = ('Updates empty values of default translation fields using'
            ' values from original fields (in all translated models).')

    def handle(self, **options):
        verbosity = int(options['verbosity'])
        if verbosity > 0:
            self.stdout.write(
                "Using default language: %s\n" % DEFAULT_LANGUAGE)
        models = translator.get_registered_models(abstract=False)
        for model in models:
            if verbosity > 0:
                self.stdout.write("Updating data of model '%s'\n" % model)
            opts = translator.get_options_for_model(model)
            for field_name in opts.fields.keys():
                def_lang_fieldname = build_localized_fieldname(
                    field_name, DEFAULT_LANGUAGE)

                # We'll only update fields which do not have an existing value
                q = Q(**{def_lang_fieldname: None})
                field = model._meta.get_field(field_name)
                if field.empty_strings_allowed:
                    q |= Q(**{def_lang_fieldname: ''})

                if issubclass(model, Page):
                    # patching Page.full_clean() to avoid validation errors due to 'slug_xx' and 'title_xx' absences
                    original_full_clean = model.full_clean
                    model.full_clean = lambda *args: None

                    for obj in model._default_manager.filter(q):
                        original_field = obj.__dict__.get(field_name)  # retrieve original untranslated value
                        setattr(obj, def_lang_fieldname, original_field)
                        obj.save(update_fields=[def_lang_fieldname])

                    model.full_clean = original_full_clean
                else:
                    model._default_manager.filter(q).rewrite(False).update(
                        **{def_lang_fieldname: F(field_name)})
