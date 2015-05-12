# coding: utf-8

from django.conf import settings
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from modeltranslation.translator import translator, NotRegistered


####################################
# TRANSLATION MIXIN
####################################
class TranslationMixin(object):

    def __init__(self, *args, **kwargs):
        super(TranslationMixin, self).__init__(*args, **kwargs)

        self.translation_options = translator.get_options_for_model(
            self.__class__)

        self.patch_translation_panels()

    def patch_translation_panels(self):
        if hasattr(self, 'panels'):
            # TODO !!!!
            tabs = ()
        else:
            tabs = ()

            if hasattr(self, 'content_panels'):
                tabs += (('content_panels', list(self.content_panels)),)
            if hasattr(self, 'promote_panels'):
                tabs += (('promote_panels', list(self.promote_panels)),)

        for tab_name, tab in tabs:
            translated_tab = []
            for panel in tab:
                ####################################
                # FIELDPANEL
                ####################################
                if panel.__class__.__name__ == 'FieldPanel':
                    for item in self.patch_translation_field(panel):
                        translated_tab.append(item)
                ####################################
                # MULTIFIELDPANEL
                ####################################
                elif panel.__class__.__name__ == 'MultiFieldPanel':
                    translated_children = []
                    for child_panel in panel.children:
                        for item in self.patch_translation_field(child_panel):
                            translated_children.append(item)
                    translated_tab.append(
                        MultiFieldPanel(
                            translated_children,
                            classname=panel.classname,
                            heading=panel.heading))
                ####################################
                # INLINEPANEL
                ####################################
                elif panel.__class__.__name__ == 'InlinePanel':
                    self.patch_translation_inlinepanels(panel)
                    translated_tab.append(panel)
                ####################################
                # OTHERS
                ####################################
                else:
                    translated_tab.append(panel)

            setattr(self.__class__, tab_name, translated_tab)

    def patch_translation_field(self, fieldpanel, translation_fields=None):
        translated_fields = []
        tr_fields = translation_fields if translation_fields else self.translation_options.fields

        translated_fields.append(fieldpanel)  # default language or untranslated field
        if fieldpanel.field_name in tr_fields:
            for lang in settings.LANGUAGES:
                if lang[0] != settings.LANGUAGE_CODE:  # other languages
                        translated_field_name = "%s_%s" % (
                            fieldpanel.field_name, lang[0])
                        translated_fields.append(
                            FieldPanel(
                                translated_field_name,
                                classname=fieldpanel.classname))

        return translated_fields

    def patch_translation_inlinepanels(self, panel):
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
            if inlinepanel.__class__.__name__ == 'FieldPanel':
                for item in self.patch_translation_field(
                        inlinepanel,
                        translation_fields=inline_model_tr_fields):
                    translated_inline.append(item)
            elif inlinepanel.__class__.__name__ == 'MultiFieldPanel':
                translated_children = []
                for child_panel in inlinepanel.children:
                    for item in self.patch_translation_field(
                            child_panel,
                            translation_fields=inline_model_tr_fields):
                        translated_children.append(item)
                translated_inline.append(
                    MultiFieldPanel(
                        translated_children,
                        classname=inlinepanel.classname,
                        heading=inlinepanel.heading))
            else:
                translated_inline.append(inlinepanel)

        getattr(self.__class__, panel.relation_name).related.model.panels = translated_inline
