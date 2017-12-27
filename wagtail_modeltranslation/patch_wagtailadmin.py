# coding: utf-8
import copy
import logging
import types

from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db import transaction, connection
from django.http import Http404
from django.utils.translation import trans_real
from django.utils.translation import ugettext_lazy as _
from modeltranslation import settings as mt_settings
from modeltranslation.translator import translator, NotRegistered
from modeltranslation.utils import build_localized_fieldname, get_language
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.views import get_setting_edit_handler
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin
from wagtail.wagtailadmin.edit_handlers import FieldPanel, \
    MultiFieldPanel, FieldRowPanel, InlinePanel, StreamFieldPanel, RichTextFieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField, StreamValue
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch.index import SearchField
from wagtail.wagtailsnippets.models import get_snippet_models
from wagtail.wagtailsnippets.views.snippets import SNIPPET_EDIT_HANDLERS

from wagtail_modeltranslation.settings import CUSTOM_SIMPLE_PANELS, CUSTOM_COMPOSED_PANELS, ORIGINAL_SLUG_LANGUAGE
from wagtail_modeltranslation.utils import compare_class_tree_depth

logger = logging.getLogger('wagtail.core')

SIMPLE_PANEL_CLASSES = [FieldPanel, ImageChooserPanel, StreamFieldPanel, RichTextFieldPanel] + CUSTOM_SIMPLE_PANELS
COMPOSED_PANEL_CLASSES = [MultiFieldPanel, FieldRowPanel] + CUSTOM_COMPOSED_PANELS


class WagtailTranslator(object):
    _patched_models = []

    def __init__(self, model):
        # Check if this class was already patched
        if model in WagtailTranslator._patched_models:
            return

        self.patched_model = model

        if issubclass(model, Page):
            self._patch_page_models(model)
        else:
            self._patch_other_models(model)

        WagtailTranslator._patched_models.append(model)

    def _patch_page_models(self, model):
        # PANEL PATCHING

        # Check if the model has a custom edit handler
        if hasattr(model, 'edit_handler'):
            tabs = model.edit_handler.children

            for tab in tabs:
                tab.children = self._patch_panels(tab.children)

        else:
            # If the page doesn't have an edit_handler we patch the panels that
            # wagtail uses by default

            if hasattr(model, 'content_panels'):
                model.content_panels = self._patch_panels(model.content_panels)
            if hasattr(model, 'promote_panels'):
                model.promote_panels = self._patch_panels(model.promote_panels)
            if hasattr(model, 'settings_panels'):
                model.settings_panels = self._patch_panels(model.settings_panels)

        # Clear the edit handler cached value, if it exists, so wagtail reconstructs
        # the edit_handler based on the patched panels
        model.get_edit_handler.cache_clear()

        # SEARCH FIELDS PATCHING

        translation_registered_fields = translator.get_options_for_model(model).fields

        for field in model.search_fields:
            # Check if the field is a SearchField and if it is one of the fields registered for translation
            if field.__class__ is SearchField and field.field_name in translation_registered_fields:
                # If it is we create a clone of the original SearchField to keep all the defined options
                # and replace its name by the translated one
                for language in mt_settings.AVAILABLE_LANGUAGES:
                    translated_field = copy.deepcopy(field)
                    translated_field.field_name = build_localized_fieldname(field.field_name, language)
                    model.search_fields = list(model.search_fields) + [translated_field]

        # OVERRIDE FIELDS
        model_fields = model._meta.get_fields()
        for field in model_fields:
            if isinstance(field, StreamField) and field.name in translation_registered_fields:
                descriptor = getattr(model, field.name)
                _patch_stream_field_meaningful_value(descriptor)

        # SLUG FIELD PATCHING
        try:
            slug_field = model._meta.get_field('slug')
            _patch_pre_save(slug_field)
        except FieldDoesNotExist:
            pass

        # OVERRIDE PAGE METHODS
        model.set_url_path = _new_set_url_path
        model.route = _new_route
        _patch_clean(model)

        if not model.save.__name__.startswith('localized'):
            setattr(model, 'save', LocalizedSaveDescriptor(model.save))

    def _patch_other_models(self, model):
        if hasattr(model, 'edit_handler'):
            edit_handler = model.edit_handler
            for tab in edit_handler:
                tab.children = self._patch_panels(tab.children)
        elif hasattr(model, 'panels'):
            model.panels = self._patch_panels(model.panels)

        if model in get_snippet_models() and model in SNIPPET_EDIT_HANDLERS:
            del SNIPPET_EDIT_HANDLERS[model]
        else:
            get_setting_edit_handler.cache_clear()

    def _patch_panels(self, panels_list, related_model=None):
        """
            Patching of the admin panels. If we're patching an InlinePanel panels we must provide
             the related model for that class, otherwise its used the model passed on init.
        """
        patched_panels = []
        current_patching_model = related_model or self.patched_model

        for panel in panels_list:
            if panel.__class__ in SIMPLE_PANEL_CLASSES:
                patched_panels += self._patch_simple_panel(current_patching_model, panel)
            elif panel.__class__ in COMPOSED_PANEL_CLASSES:
                patched_panels.append(self._patch_composed_panel(panel, related_model))
            elif panel.__class__ == InlinePanel:
                patched_panels.append(self._patch_inline_panel(panel))
            else:
                patched_panels.append(panel)

        return patched_panels

    def _patch_simple_panel(self, model, original_panel):
        panel_class = original_panel.__class__
        translated_panels = []
        translation_registered_fields = translator.get_options_for_model(model).fields

        # If the panel field is not registered for translation
        # the original one is returned
        if original_panel.field_name not in translation_registered_fields:
            return [original_panel]

        for language in mt_settings.AVAILABLE_LANGUAGES:
            original_field = model._meta.get_field(original_panel.field_name)
            localized_field_name = build_localized_fieldname(original_panel.field_name, language)

            # if the original field is required and the current language is the default one
            # this field's blank property is set to False
            if not original_field.blank and language == mt_settings.DEFAULT_LANGUAGE:
                localized_field = model._meta.get_field(localized_field_name)
                localized_field.blank = False

            localized_panel = panel_class(localized_field_name)

            # Pass the original panel extra attributes to the localized
            if hasattr(original_panel, 'classname'):
                localized_panel.classname = original_panel.classname
            if hasattr(original_panel, 'widget'):
                localized_panel.widget = original_panel.widget

            translated_panels.append(localized_panel)

        return translated_panels

    def _patch_composed_panel(self, original_panel, related_model=None):
        panel_class = original_panel.__class__
        patched_children_panels = self._patch_panels(original_panel.children, related_model)

        localized_panel = panel_class(patched_children_panels)

        # Pass the original panel extra attributes to the localized
        if hasattr(original_panel, 'classname'):
            localized_panel.classname = original_panel.classname
        if hasattr(original_panel, 'heading'):
            localized_panel.heading = original_panel.heading

        return localized_panel

    def _patch_inline_panel(self, panel):
        # get the model relation through the panel relation_name which is the
        # inline model related_name
        relation = getattr(self.patched_model, panel.relation_name)

        try:
            related_model = relation.rel.related_model
        except AttributeError:
            # Django 1.8
            related_model = relation.related.related_model

        # If the related model is not registered for translation there is nothing
        # for us to do
        try:
            translator.get_options_for_model(related_model)
        except NotRegistered:
            pass
        else:
            related_model.panels = self._patch_panels(getattr(related_model, 'panels', []), related_model)

        # The original panel is returned as only the related_model panels need to be
        # patched, leaving the original untouched
        return panel

# Overridden Page methods adapted to the translated fields


def _new_set_url_path(self, parent):
    """
    This method override populates url_path for each specified language.
    This way we can get different urls for each language, defined
    by page slug.
    """
    for language in mt_settings.AVAILABLE_LANGUAGES:
        localized_slug_field = build_localized_fieldname('slug', language)
        default_localized_slug_field = build_localized_fieldname('slug', mt_settings.DEFAULT_LANGUAGE)
        localized_url_path_field = build_localized_fieldname('url_path', language)
        default_localized_url_path_field = build_localized_fieldname('url_path', mt_settings.DEFAULT_LANGUAGE)

        if parent:
            # Emulate the default behavior of django-modeltranslation to get the slug and url path
            # for the current language. If the value for the current language is invalid we get the one
            # for the default fallback language
            slug = getattr(self, localized_slug_field, None) or \
                   getattr(self, default_localized_slug_field, None) or self.slug
            parent_url_path = getattr(parent, localized_url_path_field, None) or \
                              getattr(parent, default_localized_url_path_field, None) or parent.url_path

            setattr(self, localized_url_path_field, parent_url_path + slug + '/')

        else:
            # a page without a parent is the tree root,
            # which always has a url_path of '/'
            setattr(self, localized_url_path_field, '/')

    return self.url_path


def _new_route(self, request, path_components):
    """
    Rewrite route method in order to handle languages fallbacks
    """
    # copied from wagtail/contrib/wagtailroutablepage/models.py mixin ##
    # Override route when Page is also RoutablePage
    if isinstance(self, RoutablePageMixin):
        if self.live:
            try:
                path = '/'
                if path_components:
                    path += '/'.join(path_components) + '/'

                view, args, kwargs = self.resolve_subpage(path)
                return RouteResult(self, args=(view, args, kwargs))
            except Http404:
                pass

    if path_components:
        # request is for a child of this page
        child_slug = path_components[0]
        remaining_components = path_components[1:]

        subpages = self.get_children()
        for page in subpages:
            if page.slug == child_slug:
                return page.specific.route(request, remaining_components)
        raise Http404

    else:
        # request is for this very page
        if self.live:
            return RouteResult(self)
        else:
            raise Http404


def _validate_slugs(page):
    """
    Determine whether the given slug is available for use on a child page of
    parent_page.
    """
    parent_page = page.get_parent()

    if parent_page is None:
        # the root page's slug can be whatever it likes...
        return {}

    # Save the current active language
    current_language = get_language()

    siblings = page.get_siblings(inclusive=False)

    errors = {}

    for language in mt_settings.AVAILABLE_LANGUAGES:
        # Temporarily activate every language because even though there might
        # be no repeated value for slug_pt the fallback of an empty slug could
        # already be in use

        trans_real.activate(language)

        siblings_slugs = [sibling.slug for sibling in siblings]

        if page.slug in siblings_slugs:
            errors[build_localized_fieldname('slug', language)] = _("This slug is already in use")

    # Re-enable the original language
    trans_real.activate(current_language)

    return errors


def _patch_clean(model):
    old_clean = model.clean

    def clean(self):
        errors = _validate_slugs(self)

        if errors:
            raise ValidationError(errors)

        # Call the original clean method to avoid losing validations
        old_clean(self)

    model.clean = clean


def _localized_update_descendant_url_paths(page, old_url_path, new_url_path, language):
    localized_url_path = build_localized_fieldname('url_path', language)

    cursor = connection.cursor()
    if connection.vendor == 'sqlite':
        update_statement = """
            UPDATE wagtailcore_page
            SET {localized_url_path} = %s || substr({localized_url_path}, %s)
            WHERE path LIKE %s AND id <> %s
        """.format(localized_url_path=localized_url_path)
    elif connection.vendor == 'mysql':
        update_statement = """
            UPDATE wagtailcore_page
            SET {localized_url_path}= CONCAT(%s, substring({localized_url_path}, %s))
            WHERE path LIKE %s AND id <> %s
        """.format(localized_url_path=localized_url_path)
    elif connection.vendor in ('mssql', 'microsoft'):
        update_statement = """
            UPDATE wagtailcore_page
            SET {localized_url_path}= CONCAT(%s, (SUBSTRING({localized_url_path}, 0, %s)))
            WHERE path LIKE %s AND id <> %s
        """.format(localized_url_path=localized_url_path)
    else:
        update_statement = """
            UPDATE wagtailcore_page
            SET {localized_url_path} = %s || substring({localized_url_path} from %s)
            WHERE path LIKE %s AND id <> %s
        """.format(localized_url_path=localized_url_path)
    cursor.execute(update_statement, [new_url_path, len(old_url_path) + 1, page.path + '%', page.id])


def _new_update_descendant_url_paths(old_record, page):
    # update children paths, must be done for all languages to ensure fallbacks are applied
    default_localized_url_path = build_localized_fieldname('url_path', mt_settings.DEFAULT_LANGUAGE)
    for language in mt_settings.AVAILABLE_LANGUAGES:
        localized_url_path = build_localized_fieldname('url_path', language)
        old_url_path = getattr(old_record, localized_url_path) or getattr(old_record, default_localized_url_path)
        new_url_path = getattr(page, localized_url_path) or getattr(page, default_localized_url_path)

        if old_url_path == new_url_path:
            # nothing to do
            continue

        _localized_update_descendant_url_paths(page, old_url_path, new_url_path, language)
        update_untranslated_descendants_url_paths(page, language)


def update_untranslated_descendants_url_paths(page, language):
    localized_url_path = build_localized_fieldname('url_path', language)
    # let's restrict the query to children who don't have localized_url_path set yet
    children = page.get_children().filter(**{localized_url_path: None})
    for child in children:
        child.set_url_path(page)
        child.save()  # this will trigger any required saves downstream


class LocalizedSaveDescriptor(object):
    def __init__(self, f):
        self.func = f
        self.__name__ = 'localized_{}'.format(f.__name__)

    @transaction.atomic  # only commit when all descendants are properly updated
    def __call__(self, instance, *args, **kwargs):
        # when updating, save doesn't check if slug_xx has changed so it can only detect changes in slug
        # from current language. We need to ensure that if a given localized slug changes we call set_url_path
        if not instance.id:  # creating a record, wagtail will call set_url_path, nothing to do.
            return self.func(instance, *args, **kwargs)

        old_record = None
        changed_localized_slugs = []
        changed_localized_url_path = False
        for language in mt_settings.AVAILABLE_LANGUAGES:
            localized_slug = build_localized_fieldname('slug', language)
            localized_url_path = build_localized_fieldname('url_path', language)
            # similar logic used in save
            if not ('update_fields' in kwargs and localized_slug not in kwargs['update_fields']):
                old_record = old_record or instance.__class__.objects.get(id=instance.id)
                if getattr(old_record, localized_slug) != getattr(instance, localized_slug):
                    changed_localized_slugs.append(language)
                    continue

                # untranslated pages may have have their url_path_xx changed upstream
                # when a parent has its slug_xx changed. If that's the case let's
                # propagate the change to children
                if not getattr(instance, localized_slug) and \
                        getattr(old_record, localized_url_path) != getattr(instance, localized_url_path):
                    changed_localized_url_path = True

        # if any language other than current language had it slug changed
        # we'll execute set_url_path
        if len(changed_localized_slugs) > 1 or \
            (len(changed_localized_slugs) == 1 and changed_localized_slugs[0] != get_language()):
            instance.set_url_path(instance.get_parent())

        result = self.func(instance, *args, **kwargs)

        # update children localized paths if any language had it slug changed
        if changed_localized_slugs or changed_localized_url_path:
            _new_update_descendant_url_paths(old_record, instance)

        return result

    def __get__(self, instance, owner=None):
        return types.MethodType(self, instance) if instance else self


def _patch_stream_field_meaningful_value(field):
    old_meaningful_value = field.meaningful_value

    def meaningful_value(self, val, undefined):
        """
            Check if val is considered non-empty.
        """
        if isinstance(val, StreamValue):
            return len(val.stream_data) != 0
        return old_meaningful_value(self, val, undefined)

    field.meaningful_value = meaningful_value.__get__(field)


def _patch_pre_save(field):
    if not ORIGINAL_SLUG_LANGUAGE:
        return

    if ORIGINAL_SLUG_LANGUAGE == 'default':
        reference_slug_language = mt_settings.DEFAULT_LANGUAGE
    else:
        reference_slug_language = ORIGINAL_SLUG_LANGUAGE

    def pre_save(self, model_instance, add):
        """
        Returns slug field's value using the language set by `WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE`
        just before saving.
        """
        current_language = get_language()
        # using ORIGINAL_SLUG_LANGUAGE makes Page's slug value consistent
        trans_real.activate(reference_slug_language)
        value = getattr(model_instance, self.attname)
        trans_real.activate(current_language)
        return value

    field.pre_save = pre_save.__get__(field)


def patch_wagtail_models():
    # After all models being registered the Page or BaseSetting subclasses and snippets are patched
    registered_models = translator.get_registered_models()

    # We need to sort the models to ensure that subclasses of a model are registered first,
    # or else if the panels are inherited all the changes on the subclass would be
    # reflected in the superclass
    registered_models.sort(key=compare_class_tree_depth)

    for model_class in registered_models:
        if issubclass(model_class, Page) or model_class in get_snippet_models() or issubclass(model_class, BaseSetting):
            WagtailTranslator(model_class)
