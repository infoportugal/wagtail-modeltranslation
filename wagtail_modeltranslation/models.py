# -*- coding: utf-8 -*-
import django
import copy

from django.conf import settings
from django.http import Http404
from django.db.models import Q

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel,\
    MultiFieldPanel, FieldRowPanel
from wagtail.wagtailadmin.views.pages import get_page_edit_handler,\
    PAGE_EDIT_HANDLERS
from wagtail.wagtailsnippets.views.snippets import get_snippet_edit_handler,\
    SNIPPET_EDIT_HANDLERS
from wagtail.wagtailcore.url_routing import RouteResult
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel

from wagtail_modeltranslation.translator import translator, NotRegistered


def autodiscover():
    """
    Auto-discover INSTALLED_APPS translation.py modules and fail silently when
    not present. This forces an import on them to register.
    Also import explicit modules.
    """
    import os
    import sys
    import copy
    from django.conf import settings
    from django.utils.module_loading import module_has_submodule
    from wagtail_modeltranslation.translator import translator
    from wagtail_modeltranslation.settings import TRANSLATION_FILES, DEBUG

    if django.VERSION < (1, 7):
        from django.utils.importlib import import_module
        mods = [(app, import_module(app)) for app in settings.INSTALLED_APPS]
    else:
        from importlib import import_module
        from django.apps import apps
        mods = [(app_config.name, app_config.module) for app_config in apps.get_app_configs()]

    for (app, mod) in mods:
        # Attempt to import the app's translation module.
        module = '%s.translation' % app
        before_import_registry = copy.copy(translator._registry)
        try:
            import_module(module)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            translator._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an translation module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'translation'):
                raise

    for module in TRANSLATION_FILES:
        import_module(module)

    # In debug mode, print a list of registered models and pid to stdout.
    # Note: Differing model order is fine, we don't rely on a particular
    # order, as far as base classes are registered before subclasses.
    if DEBUG:
        try:
            if sys.argv[1] in ('runserver', 'runserver_plus'):
                models = translator.get_registered_models()
                names = ', '.join(m.__name__ for m in models)
                print('wagtail_modeltranslation: Registered %d models for translation'
                      ' (%s) [pid: %d].' % (len(models), names, os.getpid()))
        except IndexError:
            pass


def handle_translation_registrations(*args, **kwargs):
    """
    Ensures that any configuration of the TranslationOption(s) are handled when
    importing wagtail_modeltranslation.

    This makes it possible for scripts/management commands that affect models
    but know nothing of wagtail_modeltranslation.
    """
    from wagtail_modeltranslation.settings import ENABLE_REGISTRATIONS

    if not ENABLE_REGISTRATIONS:
        # If the user really wants to disable this, they can, possibly at their
        # own expense. This is generally only required in cases where other
        # apps generate import errors and requires extra work on the user's
        # part to make things work.
        return

    # Trigger autodiscover, causing any TranslationOption initialization
    # code to execute.
    autodiscover()


if django.VERSION < (1, 7):
    handle_translation_registrations()


# WAGTAIL MODELTRANSLATION MIXIN
####################################
class TranslationMixin(object):
    _translation_options = None
    _wgform_class = None
    _translated = False
    _required_fields = []

    def __init__(self, *args, **kwargs):
        super(TranslationMixin, self).__init__(*args, **kwargs)

        TranslationMixin._translation_options = translator.\
            get_options_for_model(
                self.__class__)

        if self.__class__._translated:
            return

        # CONSTRUCT TEMPORARY EDIT HANDLER
        if issubclass(self.__class__, Page):
            edit_handler_class = get_page_edit_handler(self.__class__)
        else:
            edit_handler_class = get_snippet_edit_handler(self.__class__)
        TranslationMixin._wgform_class = edit_handler_class.get_form_class(
            self.__class__)

        defined_tabs = TranslationMixin._fetch_defined_tabs(self.__class__)

        for tab_name, tab in defined_tabs:
            patched_tab = []

            for panel in tab:
                trtab = TranslationMixin._patch_panel(self, panel)

                if trtab:
                    for x in trtab:
                        patched_tab.append(x)

            setattr(self.__class__, tab_name, patched_tab)

        # DELETE TEMPORARY EDIT HANDLER IN ORDER TO LET WAGTAIL RECONSTRUCT
        # NEW EDIT HANDLER BASED ON NEW TRANSLATION PANELS
        if issubclass(self.__class__, Page):
            if self.__class__ in PAGE_EDIT_HANDLERS:
                del PAGE_EDIT_HANDLERS[self.__class__]
            edit_handler_class = get_page_edit_handler(self.__class__)
        else:
            if self.__class__ in SNIPPET_EDIT_HANDLERS:
                del SNIPPET_EDIT_HANDLERS[self.__class__]
            edit_handler_class = get_snippet_edit_handler(self.__class__)

        form = edit_handler_class.get_form_class(self.__class__)
        for fname, f in form.base_fields.items():
            # set field required on formset level if original field is required
            # as well
            if fname in self._required_fields:
                f.required = True

            if fname in TranslationMixin._translation_options.fields and TranslationMixin._is_orig_required(fname):
                f.required = False

        self.__class__._translated = True

    @staticmethod
    def _fetch_defined_tabs(defined_class):
        """
        Fetch tabs defined by user in models.py
        """
        tabs = ()

        # If user has defined panels dict on models.py
        if hasattr(defined_class, 'panels'):
            # TEST !!!
            tabs += (('panels',
                      copy.deepcopy(defined_class.panels)),)
        # Check for common tabs
        else:
            if hasattr(defined_class, 'content_panels'):
                tabs += (('content_panels',
                          copy.deepcopy(defined_class.content_panels)),)
            if hasattr(defined_class, 'promote_panels'):
                tabs += (('promote_panels',
                          copy.deepcopy(defined_class.promote_panels)),)
            if hasattr(defined_class, 'settings_panels'):
                tabs += (('settings_panels',
                          copy.deepcopy(defined_class.settings_panels)),)

        return tabs

    @staticmethod
    def _patch_panel(instance, panel, inline_tr_options=None):
        """
        Generic panel patching function
        """
        trpanels = None

        if panel.__class__.__name__ == 'FieldPanel':
            trpanels = TranslationMixin._patch_fieldpanel(
                panel, inline_tr_options)
        elif panel.__class__.__name__ == 'MultiFieldPanel':
            trpanels = [TranslationMixin._patch_multifieldpanel(
                panel, inline_tr_options)]
        elif panel.__class__.__name__ == 'InlinePanel':
            TranslationMixin._patch_inlinepanel(instance, panel)
            trpanels = [panel]
        elif panel.__class__.__name__ == 'StreamFieldPanel':
            trpanels = TranslationMixin._patch_streamfieldpanel(panel)
        else:
            trpanels = [panel]

        return trpanels

    @classmethod
    def _is_orig_required(cls, field_name, formset=None):
        """
        check if original field is required
        TODO:
        if formset is given, example for inline models.
        """
        required = False

        if not formset:
            for fname, f in cls._wgform_class.base_fields.items():
                if fname == field_name:
                    if f.required:
                        required = True
                    break

        return required

    # FieldPanel
    ####################################
    @classmethod
    def _patch_fieldpanel(cls, fieldpanel, inline_tr_options=None):
        """
        Patch FieldPanels and return one per available language
        """
        tr_fields = []
        if inline_tr_options:
            tr_fields = inline_tr_options
        else:
            tr_fields = cls._translation_options.fields

        translated_fieldpanels = []
        if fieldpanel.field_name in tr_fields:
            for lang in settings.LANGUAGES:
                classes = fieldpanel.classname

                if cls._is_orig_required(fieldpanel.field_name) and\
                   (lang[0] == settings.LANGUAGE_CODE):
                    if ("%s_%s" % (fieldpanel.field_name, lang[0]) not in cls._required_fields):
                        cls._required_fields.append("%s_%s" % (
                                fieldpanel.field_name, lang[0]))

                translated_field_name = "%s_%s" % (
                        fieldpanel.field_name, lang[0])
                translated_fieldpanels.append(
                    FieldPanel(
                        translated_field_name,
                        classname=classes))

            # delete original field from form
            if fieldpanel.field_name in cls._wgform_class._meta.fields:
                cls._wgform_class._meta.fields.remove(fieldpanel.field_name)
        else:
            return [fieldpanel]

        return translated_fieldpanels

    # StreamFieldPanel
    ####################################
    @classmethod
    def _patch_streamfieldpanel(cls, fieldpanel, inline_tr_options=None):
        """
        Patch StreamFieldPanels and return one per available language
        """
        tr_fields = []
        if inline_tr_options:
            tr_fields = inline_tr_options
        else:
            tr_fields = cls._translation_options.fields

        translated_fieldpanels = []
        if fieldpanel.field_name in tr_fields:
            for lang in settings.LANGUAGES:
                if cls._is_orig_required(fieldpanel.field_name) and\
                   (lang[0] == settings.LANGUAGE_CODE):
                    if ("%s_%s" % (fieldpanel.field_name, lang[0]) not in cls._required_fields):
                        cls._required_fields.append("%s_%s" % (
                                fieldpanel.field_name, lang[0]))

                translated_field_name = "%s_%s" % (
                        fieldpanel.field_name, lang[0])
                translated_fieldpanels.append(
                    StreamFieldPanel(
                        translated_field_name))

            # delete original field from form
            if fieldpanel.field_name in cls._wgform_class._meta.fields:
                cls._wgform_class._meta.fields.remove(fieldpanel.field_name)
        else:
            return [fieldpanel]

        return translated_fieldpanels

    @classmethod
    def _patch_multifieldpanel(cls, mfpanel, inline_tr_options=None):
        """
        Patch MultiFieldPanel
        """
        patched_fields = []

        for panel in mfpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in cls._patch_fieldpanel(panel, inline_tr_options):
                    patched_fields.append(item)
            elif panel.__class__.__name__ == 'FieldRowPanel':
                patched_fields.append(
                    cls._patch_fieldrowpanel(panel, inline_tr_options))
            else:
                patched_fields.append(panel)

        return MultiFieldPanel(
            patched_fields,
            classname=mfpanel.classname,
            heading=mfpanel.heading)

    @classmethod
    def _patch_fieldrowpanel(cls, frpanel, inline_tr_options=None):
        """
        Patch FieldRowPanel
        """
        patched_fields = []

        for panel in frpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in cls._patch_fieldpanel(panel, inline_tr_options):
                    patched_fields.append(item)
            else:
                patched_fields.append(panel)

        return FieldRowPanel(
            patched_fields,
            classname=frpanel.classname)

    @classmethod
    def _patch_inlinepanel(cls, instance, panel):
        relation = getattr(instance.__class__, panel.relation_name)
        inline_panels = getattr(relation.related.model, 'panels', [])
        try:
            inline_model_tr_fields = translator.get_options_for_model(
                getattr(
                    instance.__class__, panel.relation_name).related.model).fields
        except NotRegistered:
            return None

        translated_inline = []
        for inlinepanel in inline_panels:
            for item in cls._patch_fieldpanel(inlinepanel, inline_model_tr_fields):
                translated_inline.append(item)

        getattr(instance.__class__, panel.relation_name).related.model.panels = translated_inline

    def set_url_path(self, parent):
        """
        This method override populates url_path for each specified language.
        This way we can get different urls for each language, defined
        by page slug.
        """

        for lang in settings.LANGUAGES:
            if parent:
                tr_slug = getattr(self, 'slug_'+lang[0])
                if not tr_slug:
                    tr_slug = getattr(self, 'slug_'+settings.LANGUAGE_CODE)

                parent_url_path = getattr(parent, 'url_path_'+lang[0])

                if not parent_url_path:
                    parent_url_path = getattr(parent, 'url_path')

                setattr(self, 'url_path_'+lang[0], parent_url_path + tr_slug + '/')
            else:
                # a page without a parent is the tree root,
                # which always has a url_path of '/'
                setattr(self, 'url_path_'+lang[0], '/')

        return self.url_path

    def route(self, request, path_components):
        """
        Rewrite route method in order to handle languages fallbacks
        """
        if path_components:
            # request is for a child of this page
            child_slug = path_components[0]
            remaining_components = path_components[1:]

            try:
                q = Q()
                for lang in settings.LANGUAGES:
                    tr_field_name = 'slug_%s' % (lang[0])
                    condition = {tr_field_name: child_slug}
                    q |= Q(**condition)
                subpage = self.get_children().get(q)
            except Page.DoesNotExist:
                raise Http404

            return subpage.specific.route(request, remaining_components)

        else:
            # request is for this very page
            if self.live:
                return RouteResult(self)
            else:
                raise Http404

    @staticmethod
    def get_site_root_paths():
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

    def relative_url(self, current_site):
        """
        Return the 'most appropriate' URL for this page taking into account the site we're currently on;
        a local URL if the site matches, or a fully qualified one otherwise.
        Return None if the page is not routable.

        Override for using TranslationMixin.get_site_root_paths() insted of
        Site.get_site_root_paths()
        """
        for (id, root_path, root_url) in TranslationMixin.get_site_root_paths():
            if self.url_path.startswith(root_path):
                return ('' if current_site.id == id else root_url) + reverse('wagtail_serve', args=(self.url_path[len(root_path):],))


    @property
    def url(self):
        """
        Return the 'most appropriate' URL for referring to this page from the pages we serve,
        within the Wagtail backend and actual website templates;
        this is the local URL (starting with '/') if we're only running a single site
        (i.e. we know that whatever the current page is being served from, this link will be on the
        same domain), and the full URL (with domain) if not.
        Return None if the page is not routable.

        Override for using TranslationMixin.get_site_root_paths() insted of
        Site.get_site_root_paths()
        """
        root_paths = TranslationMixin.get_site_root_paths()

        for (id, root_path, root_url) in root_paths:
            if self.url_path.startswith(root_path):
                return ('' if len(root_paths) == 1 else root_url) + reverse('wagtail_serve', args=(self.url_path[len(root_path):],))
