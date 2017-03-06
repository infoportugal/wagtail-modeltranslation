# -*- coding: utf-8 -*-
import copy
import logging
import operator

from six import iteritems

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext as _
from wagtail.wagtailadmin.edit_handlers import FieldPanel, \
    MultiFieldPanel, FieldRowPanel
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch.index import SearchField
from wagtail.wagtailsnippets.views.snippets import get_snippet_edit_handler, \
    SNIPPET_EDIT_HANDLERS
from wagtail_modeltranslation.translator import translator, NotRegistered
from .utils import build_localized_fieldname

try:
    from wagtail.wagtailadmin.views.pages import get_page_edit_handler, \
        PAGE_EDIT_HANDLERS
except ImportError:
    pass

try:
    from functools import reduce
except ImportError:
    pass

logger = logging.getLogger('wagtail.core')


class WagtailTranslator(object):
    _patched_models = []

    def __init__(self, model):

        # Check if this class was already patched
        if model in WagtailTranslator._patched_models:
            return

        WagtailTranslator._base_model = model
        WagtailTranslator._required_fields = {}

        # CONSTRUCT TEMPORARY EDIT HANDLER
        if issubclass(model, Page):
            if hasattr(model, 'get_edit_handler'):
                edit_handler_class = model.get_edit_handler()
            else:
                edit_handler_class = get_page_edit_handler(model)
        else:
            edit_handler_class = get_snippet_edit_handler(model)
        WagtailTranslator._base_model_form = edit_handler_class.get_form_class(model)

        defined_tabs = WagtailTranslator._fetch_defined_tabs(model)

        for tab_name, tab in defined_tabs:
            patched_tab = []

            for panel in tab:
                trtab = WagtailTranslator._patch_panel(model, panel)

                if trtab:
                    for x in trtab:
                        patched_tab.append(x)

            setattr(model, tab_name, patched_tab)

        # DELETE TEMPORARY EDIT HANDLER IN ORDER TO LET WAGTAIL RECONSTRUCT
        # NEW EDIT HANDLER BASED ON NEW TRANSLATION PANELS
        if issubclass(model, Page):
            if hasattr(model, 'get_edit_handler'):
                model.get_edit_handler.cache_clear()
                edit_handler_class = model.get_edit_handler()
            else:
                if model in PAGE_EDIT_HANDLERS:
                    del PAGE_EDIT_HANDLERS[model]
                edit_handler_class = get_page_edit_handler(model)
        else:
            if model in SNIPPET_EDIT_HANDLERS:
                del SNIPPET_EDIT_HANDLERS[model]
            edit_handler_class = get_snippet_edit_handler(model)

        # Set the required of the translated fields that were required on the original field
        form = edit_handler_class.get_form_class(model)
        for fname, f in form.base_fields.items():
            if fname in WagtailTranslator._required_fields[model]:
                f.required = True

        # Do the same to the formsets
        for related_name, formset in iteritems(form.formsets):
            if (formset.model in WagtailTranslator._required_fields and
                    WagtailTranslator._required_fields[formset.model]):
                for fname, f in formset.form.base_fields.items():
                    if fname in WagtailTranslator._required_fields[formset.model]:
                        f.required = True

        # Overide page methods
        if issubclass(model, Page):
            model.move = _new_move
            _patch_clean(model)
            _patch_elasticsearch_fields(model)

        WagtailTranslator._patched_models.append(model)

    @staticmethod
    def _fetch_defined_tabs(defined_class):
        """
        Fetch tabs defined by user in models.py
        """
        tabs = ()

        # If user has defined panels dict on models.py
        if hasattr(defined_class, 'panels'):
            # TEST !!!
            tabs += (('panels', copy.deepcopy(defined_class.panels)),)
        # Check for common tabs
        else:
            if hasattr(defined_class, 'content_panels'):
                tabs += (('content_panels', copy.deepcopy(defined_class.content_panels)),)
            if hasattr(defined_class, 'promote_panels'):
                tabs += (('promote_panels', copy.deepcopy(defined_class.promote_panels)),)
            if hasattr(defined_class, 'settings_panels'):
                tabs += (('settings_panels', copy.deepcopy(defined_class.settings_panels)),)

        return tabs

    @staticmethod
    def _patch_panel(model, panel):
        """
        Generic panel patching function
        """

        WagtailTranslator._current_model = model
        WagtailTranslator._translation_options = translator.get_options_for_model(model)
        if model not in WagtailTranslator._required_fields:
            WagtailTranslator._required_fields[model] = []

        if panel.__class__.__name__ == 'FieldPanel':
            trpanels = WagtailTranslator._patch_fieldpanel(panel)
        elif panel.__class__.__name__ == 'ImageChooserPanel':
            trpanels = WagtailTranslator._patch_imagechooser(panel)
        elif panel.__class__.__name__ == 'MultiFieldPanel':
            trpanels = [WagtailTranslator._patch_multifieldpanel(panel)]
        elif panel.__class__.__name__ == 'InlinePanel':
            WagtailTranslator._patch_inlinepanel(model, panel)
            trpanels = [panel]
        elif panel.__class__.__name__ == 'StreamFieldPanel':
            trpanels = WagtailTranslator._patch_streamfieldpanel(panel)
        elif panel.__class__.__name__ == 'FieldRowPanel':
            trpanels = [WagtailTranslator._patch_fieldrowpanel(panel)]
        else:
            trpanels = [panel]

        return trpanels

    @classmethod
    def _is_orig_required(cls, field_name):
        """
        check if original field is required
        """
        if cls._base_model == cls._current_model:
            for fname, f in cls._base_model_form.base_fields.items():
                if fname == field_name:
                    return f.required
        else:
            for related_name, formset in iteritems(cls._base_model_form.formsets):
                if formset.model == cls._current_model:
                    for fname, f in formset.form.base_fields.items():
                        if fname == field_name:
                            return f.required
                    break

        return False

    # FieldPanel
    ####################################
    @classmethod
    def _patch_fieldpanel(cls, fieldpanel):
        """
        Patch FieldPanels and return one per available language
        """

        tr_fields = cls._translation_options.fields

        translated_fieldpanels = []
        if fieldpanel.field_name in tr_fields:
            for lang in settings.LANGUAGES:
                classes = fieldpanel.classname

                if cls._is_orig_required(fieldpanel.field_name) and (lang[0] == settings.LANGUAGE_CODE):
                    if (build_localized_fieldname(fieldpanel.field_name, lang[0]) not in
                            cls._required_fields[cls._current_model]):
                        cls._required_fields[cls._current_model].append(
                            build_localized_fieldname(fieldpanel.field_name, lang[0]))

                translated_field_name = build_localized_fieldname(fieldpanel.field_name, lang[0])
                translated_fieldpanels.append(
                    FieldPanel(translated_field_name, classname=classes, widget=fieldpanel.widget)
                )

        else:
            return [fieldpanel]

        return translated_fieldpanels

    # ImageChooserPanel
    ####################################
    @classmethod
    def _patch_imagechooser(cls, imagechooser):
        """
        Patch ImageChooserPanels and return one per available language
        """
        tr_fields = cls._translation_options.fields

        translated_imagechoosers = []
        if imagechooser.field_name in tr_fields:
            for lang in settings.LANGUAGES:

                if cls._is_orig_required(imagechooser.field_name) and (lang[0] == settings.LANGUAGE_CODE):
                    if (build_localized_fieldname(imagechooser.field_name, lang[0]) not in
                            cls._required_fields[cls._current_model]):
                        cls._required_fields[cls._current_model].append(
                            build_localized_fieldname(imagechooser.field_name, lang[0])
                        )

                translated_field_name = build_localized_fieldname(imagechooser.field_name, lang[0])
                translated_imagechoosers.append(ImageChooserPanel(translated_field_name))
        else:
            return [imagechooser]

        return translated_imagechoosers

    # StreamFieldPanel
    ####################################
    @classmethod
    def _patch_streamfieldpanel(cls, fieldpanel):
        """
        Patch StreamFieldPanels and return one per available language
        """
        tr_fields = cls._translation_options.fields

        translated_fieldpanels = []
        if fieldpanel.field_name in tr_fields:
            for lang in settings.LANGUAGES:
                if cls._is_orig_required(fieldpanel.field_name) and (lang[0] == settings.LANGUAGE_CODE):
                    if (build_localized_fieldname(fieldpanel.field_name, lang[0]) not in
                            cls._required_fields[cls._current_model]):
                        cls._required_fields[cls._current_model].append(
                            build_localized_fieldname(fieldpanel.field_name, lang[0])
                        )

                translated_field_name = build_localized_fieldname(fieldpanel.field_name, lang[0])
                translated_fieldpanels.append(StreamFieldPanel(translated_field_name))
        else:
            return [fieldpanel]

        return translated_fieldpanels

    @classmethod
    def _patch_multifieldpanel(cls, mfpanel):
        """
        Patch MultiFieldPanel
        """
        patched_fields = []

        for panel in mfpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in cls._patch_fieldpanel(panel):
                    patched_fields.append(item)
            elif panel.__class__.__name__ == 'ImageChooserPanel':
                for item in cls._patch_imagechooser(panel):
                    patched_fields.append(item)
            elif panel.__class__.__name__ == 'FieldRowPanel':
                patched_fields.append(cls._patch_fieldrowpanel(panel))
            else:
                patched_fields.append(panel)

        return MultiFieldPanel(patched_fields, classname=mfpanel.classname, heading=mfpanel.heading)

    @classmethod
    def _patch_fieldrowpanel(cls, frpanel):
        """
        Patch FieldRowPanel
        """
        patched_fields = []

        for panel in frpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in cls._patch_fieldpanel(panel):
                    patched_fields.append(item)
            else:
                patched_fields.append(panel)

        return FieldRowPanel(
            patched_fields,
            classname=frpanel.classname)

    @classmethod
    def _patch_inlinepanel(cls, model, panel):
        relation = getattr(model, panel.relation_name)

        related_fieldname = 'related'

        try:
            inline_panels = getattr(getattr(relation, related_fieldname).related_model, 'panels', [])
        except AttributeError:
            related_fieldname = 'rel'
            inline_panels = getattr(getattr(relation, related_fieldname).related_model, 'panels', [])

        try:
            related_model = getattr(getattr(model, panel.relation_name), related_fieldname).related_model
            WagtailTranslator._translation_options = translator.get_options_for_model(related_model)
        except NotRegistered:
            return None
        translated_inline = []
        for inline_panel in inline_panels:
            for item in cls._patch_panel(related_model, inline_panel):
                translated_inline.append(item)

        related_model.panels = translated_inline


# Overridden Page methods adapted to the translated fields

@transaction.atomic  # only commit when all descendants are properly updated
def _new_move(self, target, pos=None):
    """
    Extension to the treebeard 'move' method to ensure that url_path is updated too.
    """
    old_url_path = Page.objects.get(id=self.id).url_path
    super(Page, self).move(target, pos=pos)
    # treebeard's move method doesn't actually update the in-memory instance, so we need to work
    # with a freshly loaded one now
    # added .specific to use the most specific class so that url_paths are updated to all languages
    new_self = Page.objects.get(id=self.id).specific
    new_url_path = new_self.set_url_path(new_self.get_parent())
    new_self.save()
    new_self._update_descendant_url_paths(old_url_path, new_url_path)

    # Log
    logger.info("Page moved: \"%s\" id=%d path=%s", self.title, self.id, new_url_path)


def _validate_slugs(page):
    """
    Determine whether the given slug is available for use on a child page of
    parent_page.
    """
    parent_page = page.get_parent()

    if parent_page is None:
        # the root page's slug can be whatever it likes...
        return {}

    allowed_sibblings = parent_page.specific.allowed_subpage_models()
    siblings = parent_page.get_children().exclude(pk=page.pk)

    errors = {}

    for lang in settings.LANGUAGES:
        current_slug = 'slug_' + lang[0]
        query_list = []

        for model in allowed_sibblings:
            slug = getattr(page, current_slug, '') or ''
            if len(slug) and model is not Page:
                if model in WagtailTranslator._patched_models:
                    field_name = '{0}__{1}'.format(model._meta.model_name, current_slug)
                else:
                    field_name = '{0}__slug'.format(model._meta.model_name)
                kwargs = {field_name: slug}
                query_list.append(Q(**kwargs))

        if query_list and siblings.filter(reduce(operator.or_, query_list)).exists():
            errors[current_slug] = _(u'Slug already in use')

    return errors


def _patch_clean(model):
    old_clean = model.clean

    # Call the original clean method to avoid losing validations
    def clean(self):
        old_clean(self)
        errors = _validate_slugs(self)

        if errors:
            raise ValidationError(errors)

    model.clean = clean


def _patch_elasticsearch_fields(model):
    for field in model.search_fields:
        # Check if the field is a SearchField and if it is one of the fields registered for translation
        if field.__class__ is SearchField and field.field_name in WagtailTranslator._translation_options.fields:
            # If it is we create a clone of the original SearchField to keep all the defined options
            # and replace its name by the translated one
            for lang in settings.LANGUAGES:
                translated_field = copy.deepcopy(field)
                translated_field.field_name = build_localized_fieldname(field.field_name, lang[0])
                model.search_fields = model.search_fields + (translated_field,)
