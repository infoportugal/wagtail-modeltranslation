# coding: utf-8

import copy

from django.conf import settings
from django.http import Http404
from django.db.models import Q

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel,\
                                               MultiFieldPanel, FieldRowPanel
from wagtail.wagtailadmin.views.pages import get_page_edit_handler,\
                                             PAGE_EDIT_HANDLERS
from wagtail.wagtailcore.url_routing import RouteResult

from modeltranslation.translator import translator, NotRegistered


####################################
# TRANSLATION MIXIN
####################################
class TranslationMixin(object):
    _translation_options = None
    _required_base_fields = None
    _defined_tabs = None
    _wgform_class = None

    def __init__(self, *args, **kwargs):
        super(TranslationMixin, self).__init__(*args, **kwargs)

        # CONSTRUCT TEMPOARY EDIT HANDLER
        edit_handler_class = get_page_edit_handler(self.__class__)
        self._wgform_class = edit_handler_class.get_form_class(self.__class__)

        self._translation_options = translator.get_options_for_model(
            self.__class__)
        self._required_base_fields = edit_handler_class._required_fields

        self._fetch_defined_tabs()

        for tab_name, tab in self._defined_tabs:
            patched_tab = []

            for panel in tab:
                trtab = self._patch_panel(panel)
                if trtab:
                    for x in trtab:
                        patched_tab.append(x)

            setattr(self.__class__, tab_name, patched_tab)

        # DELETE TEMPORARY EDIT HANDLER IN ORDER TO LET WAGTAIL RECONSTRUCT
        # NEW EDIT HANDLER BASED ON NEW TRANSLATION PANELS
        del PAGE_EDIT_HANDLERS[self.__class__]

    def _fetch_defined_tabs(self):
        """
        Fetch tabs defined by user in models.py
        """
        tabs = ()

        # If user has defined panels dict on models.py
        if hasattr(self, 'panels'):
            # TEST !!!
            tabs = self.panels
        # Check for common tabs
        else:
            if hasattr(self, 'content_panels'):
                tabs += (('content_panels',
                          copy.deepcopy(self.content_panels)),)
                self.content_panels = None
            if hasattr(self, 'promote_panels'):
                tabs += (('promote_panels',
                          copy.deepcopy(self.promote_panels)),)
                self.promote_panels = None
            if hasattr(self, 'settings_panels'):
                tabs += (('settings_panels',
                          copy.deepcopy(self.settings_panels)),)
                self.promote_panels = None

        self._defined_tabs = tabs

    def _patch_panel(self, panel, inline_tr_options=None):
        """
        Generic panel patching function
        """
        trpanels = None

        if panel.__class__.__name__ == 'FieldPanel':
            trpanels = self._patch_fieldpanel(panel, inline_tr_options)
        elif panel.__class__.__name__ == 'MultiFieldPanel':
            trpanels = [self._patch_multifieldpanel(panel, inline_tr_options)]
        elif panel.__class__.__name__ == 'InlinePanel':
            self._patch_inlinepanel(panel)
            trpanels = [panel]
        else:
            trpanels = [panel]

        return trpanels

    def _is_orig_required(self, field_name, formset=None):
        """
        check if original field is required
        """
        required = False

        if not formset:
            for fname, f in self._wgform_class.base_fields.items():
                if fname == field_name:
                    if f.required:
                        required = True
                    break

        return required

    def _patch_fieldpanel(self, fieldpanel, inline_tr_options=None):
        """
        Patch FieldPanels and return one per available language
        """
        tr_fields = []
        if inline_tr_options:
            tr_fields = inline_tr_options
        else:
            tr_fields = self._translation_options.fields

        translated_fieldpanels = []
        if fieldpanel.field_name in tr_fields:
            # original field, HIDDEN
            translated_fieldpanels.append(
                FieldPanel(
                    fieldpanel.field_name,
                    classname='visuallyhidden'))

            for lang in settings.LANGUAGES:
                classes = fieldpanel.classname

                if self._is_orig_required(fieldpanel.field_name) and\
                   (lang[0] == settings.LANGUAGE_CODE):
                    classes += ' required'
                translated_field_name = "%s_%s" % (
                        fieldpanel.field_name, lang[0])
                translated_fieldpanels.append(
                    FieldPanel(
                        translated_field_name,
                        classname=classes))
        else:
            return [fieldpanel]

        return translated_fieldpanels

    def _patch_multifieldpanel(self, mfpanel, inline_tr_options=None):
        """
        Patch MultiFieldPanel
        """
        patched_fields = []

        for panel in mfpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in self._patch_fieldpanel(panel, inline_tr_options):
                    patched_fields.append(item)
            elif panel.__class__.__name__ == 'FieldRowPanel':
                patched_fields.append(
                    self._patch_fieldrowpanel(panel, inline_tr_options))
            else:
                patched_fields.append(panel)

        return MultiFieldPanel(
            patched_fields,
            classname=mfpanel.classname,
            heading=mfpanel.heading)

    def _patch_fieldrowpanel(self, frpanel, inline_tr_options=None):
        """
        Patch FieldRowPanel
        """
        patched_fields = []

        for panel in frpanel.children:
            if panel.__class__.__name__ == 'FieldPanel':
                for item in self._patch_fieldpanel(panel, inline_tr_options):
                    patched_fields.append(item)
            else:
                patched_fields.append(panel)

        return FieldRowPanel(
            patched_fields,
            classname=frpanel.classname)

    def _patch_inlinepanel(self, panel):
        inline_panels = getattr(
            self.__class__, panel.relation_name).related.model.panels
        try:
            inline_model_tr_fields = translator.get_options_for_model(
                getattr(
                    self.__class__, panel.relation_name).related.model).fields
        except NotRegistered:
            return None

        translated_inline = []
        for inlinepanel in inline_panels:
            for item in self._patch_panel(inlinepanel, inline_model_tr_fields):
                translated_inline.append(item)

        getattr(self.__class__, panel.relation_name).related.model.panels = translated_inline

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

                setattr(self, 'url_path_'+lang[0], tr_slug + '/')
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
