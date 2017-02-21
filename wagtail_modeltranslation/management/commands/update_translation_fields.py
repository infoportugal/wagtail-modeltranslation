# coding: utf-8

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import F, Q
from modeltranslation.settings import DEFAULT_LANGUAGE
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname
from wagtail.wagtailcore.models import Page


class Command(BaseCommand):
    help = ('Updates empty values of default translation fields using'
            ' values from original fields (in all translated models).')

    def handle_noargs(self, **options):
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
                    for obj in model._default_manager.filter(q):
                        # Get table description in order to know if field is
                        # in child or parent table
                        # TODO: Tested only on PostgreSQL engine
                        db_table = model._meta.db_table
                        db_table_desc = connection.introspection. \
                            get_table_description(
                            connection.cursor(), db_table)
                        # original field in child class
                        if field_name in [x.name for x in db_table_desc]:
                            raw = model._default_manager.raw(
                                'SELECT *, %s AS original_field FROM %s \
                                 WHERE page_ptr_id=%d LIMIT 1' % (
                                    field_name, db_table, obj.page_ptr_id))[0]
                            setattr(
                                obj, def_lang_fieldname, raw.original_field)
                        # field is a foreign key
                        elif (field_name + '_id') in \
                                [x.name for x in db_table_desc]:
                            raw = model._default_manager.raw(
                                'SELECT *, %s AS original_field FROM %s \
                                 WHERE page_ptr_id=%d LIMIT 1' % (
                                    field_name + '_id',
                                    db_table,
                                    obj.page_ptr_id))[0]
                            setattr(
                                obj,
                                def_lang_fieldname + '_id',
                                raw.original_field)
                        # original field parent class
                        else:
                            raw = Page._default_manager.raw(
                                'SELECT *, %s AS original_field FROM \
                                 wagtailcore_page WHERE id=%d LIMIT 1' % (
                                    field_name, obj.page_ptr_id))[0]
                            setattr(
                                obj, def_lang_fieldname, raw.original_field)
                        obj.save(update_fields=[def_lang_fieldname])
                else:
                    model._default_manager.filter(q).rewrite(False).update(
                        **{def_lang_fieldname: F(field_name)})
