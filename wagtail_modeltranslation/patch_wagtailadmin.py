# coding: utf-8
import copy
import logging

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import Http404
from django.utils.translation import trans_real
from django.utils.translation import ugettext_lazy as _
from modeltranslation import settings as mt_settings
from modeltranslation.translator import translator, NotRegistered
from modeltranslation.utils import build_localized_fieldname, get_language
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.views import get_setting_edit_handler
from wagtail.wagtailadmin.edit_handlers import FieldPanel, \
    MultiFieldPanel, FieldRowPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch.index import SearchField
from wagtail.wagtailsnippets.models import get_snippet_models
from wagtail.wagtailsnippets.views.snippets import SNIPPET_EDIT_HANDLERS

from wagtail_modeltranslation.settings import CUSTOM_SIMPLE_PANELS, CUSTOM_COMPOSED_PANELS
from wagtail_modeltranslation.utils import compare_class_tree_depth

logger = logging.getLogger('wagtail.core')

SIMPLE_PANEL_CLASSES = [FieldPanel, ImageChooserPanel, StreamFieldPanel] + CUSTOM_SIMPLE_PANELS
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

            for tab in tabs.children:
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

        # OVERRIDE PAGE METHODS

        model.move = _new_move
        model.set_url_path = _new_set_url_path
        model.route = _new_route
        model.get_site_root_paths = _new_get_site_root_paths
        model.relative_url = _new_relative_url
        model.url = _new_url
        _patch_clean(model)

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
            parent = parent.specific

            # Emulate the default behavior of django-modeltranslation to get the slug and url path
            # for the current language. If the value for the current language is invalid we get the one
            # for the default fallback language
            slug = getattr(self, localized_slug_field, None) or getattr(self, default_localized_slug_field, self.slug)
            parent_url_path = getattr(parent, localized_url_path_field, None) or \
                              getattr(parent, default_localized_url_path_field, parent.url_path)

            setattr(self, localized_url_path_field, parent_url_path + slug + '/')

        else:
            # a page without a parent is the tree root,
            # which always has a url_path of '/'
            setattr(self, localized_url_path_field, '/')

    # update url_path for children pages
    for child in self.get_children().specific():
        child.set_url_path(self.specific)
        child.save()

    return self.url_path


def _new_route(self, request, path_components):
    """
    Rewrite route method in order to handle languages fallbacks
    """
    ## copied from wagtail/contrib/wagtailroutablepage/models.py mixin ##
    # Override route when Page is also RoutablePage
    if hasattr(self, 'resolve_subpage'):
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
            if page.specific.slug == child_slug:
                return page.specific.route(request, remaining_components)
        raise Http404

    else:
        # request is for this very page
        if self.live:
            return RouteResult(self)
        else:
            raise Http404


@staticmethod
def _new_get_site_root_paths():
    """
    Return a list of (root_path, root_url) tuples, most specific path first -
    used to translate url_paths into actual URLs with hostnames

    Same method as Site.get_site_root_paths() but without cache

    TODO: remake this method with cache and think of his integration in
    Site.get_site_root_paths()
    """
    result = [
        (site.id, site.root_page.specific.url_path, site.root_url)
        for site in Site.objects.select_related('root_page').order_by('-root_page__url_path')
        ]

    return result


def _new_relative_url(self, current_site):
    """
    Return the 'most appropriate' URL for this page taking into account the site we're currently on;
    a local URL if the site matches, or a fully qualified one otherwise.
    Return None if the page is not routable.

    Override for using custom get_site_root_paths() instead of
    Site.get_site_root_paths()
    """
    for (id, root_path, root_url) in self.get_site_root_paths():
        if self.url_path.startswith(root_path):
            return ('' if current_site.id == id else root_url) + reverse('wagtail_serve',
                                                                         args=(self.url_path[len(root_path):],))


@property
def _new_url(self):
    """
    Return the 'most appropriate' URL for referring to this page from the pages we serve,
    within the Wagtail backend and actual website templates;
    this is the local URL (starting with '/') if we're only running a single site
    (i.e. we know that whatever the current page is being served from, this link will be on the
    same domain), and the full URL (with domain) if not.
    Return None if the page is not routable.

    Override for using custom get_site_root_paths() instead of
    Site.get_site_root_paths()
    """
    root_paths = self.get_site_root_paths()

    for (id, root_path, root_url) in root_paths:
        if self.url_path.startswith(root_path):
            return ('' if len(root_paths) == 1 else root_url) + reverse(
                'wagtail_serve', args=(self.url_path[len(root_path):],))


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

    siblings = page.get_siblings(inclusive=False).specific()

    errors = {}

    for language in mt_settings.AVAILABLE_LANGUAGES:
        # Temporarily activate every language because even though there might
        # be no repeated value for slug_pt the fallback of an empty slug could
        # already be in use

        trans_real.activate(language)

        siblings_slugs = [sibling.slug for sibling in siblings]

        if page.specific.slug in siblings_slugs:
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
