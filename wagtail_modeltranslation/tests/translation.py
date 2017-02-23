# coding: utf-8
from modeltranslation.translator import translator, register, TranslationOptions

from wagtail_modeltranslation.tests.models import TestRootPage, TestSlugPage1, TestSlugPage2, PatchTestPage, \
    PatchTestSnippet, FieldPanelPage, ImageChooserPanelPage, FieldRowPanelPage, MultiFieldPanelPage, InlinePanelPage, \
    FieldPanelSnippet, ImageChooserPanelSnippet, FieldRowPanelSnippet, MultiFieldPanelSnippet, PageInlineModel, \
    BaseInlineModel, StreamFieldPanelPage, StreamFieldPanelSnippet, SnippetInlineModel, InlinePanelSnippet
from wagtail_modeltranslation.translator import WagtailTranslationOptions


# Wagtail Models

@register(TestRootPage)
class TestRootPagePageTranslationOptions(WagtailTranslationOptions):
    fields = ()


@register(TestSlugPage1)
class TestSlugPage1TranslationOptions(WagtailTranslationOptions):
    fields = ()


@register(TestSlugPage2)
class TestSlugPage2TranslationOptions(WagtailTranslationOptions):
    fields = ()


@register(PatchTestPage)
class PatchTestPageTranslationOptions(WagtailTranslationOptions):
    fields = ('description',)


class PatchTestSnippetTranslationOptions(WagtailTranslationOptions):
    fields = ('name',)


translator.register(PatchTestSnippet, PatchTestSnippetTranslationOptions)


# Panel Patching Models

class FieldPanelTranslationOptions(WagtailTranslationOptions):
    fields = ('name',)


translator.register(FieldPanelPage, FieldPanelTranslationOptions)
translator.register(FieldPanelSnippet, FieldPanelTranslationOptions)


class ImageChooserPanelTranslationOptions(WagtailTranslationOptions):
    fields = ('image',)


translator.register(ImageChooserPanelPage, ImageChooserPanelTranslationOptions)
translator.register(ImageChooserPanelSnippet, ImageChooserPanelTranslationOptions)


class FieldRowPanelTranslationOptions(WagtailTranslationOptions):
    fields = ('other_name',)


translator.register(FieldRowPanelPage, FieldRowPanelTranslationOptions)
translator.register(FieldRowPanelSnippet, FieldRowPanelTranslationOptions)


class StreamFieldPanelTranslationOptions(WagtailTranslationOptions):
    fields = ('body',)


translator.register(StreamFieldPanelPage, StreamFieldPanelTranslationOptions)
translator.register(StreamFieldPanelSnippet, StreamFieldPanelTranslationOptions)


class MultiFieldPanelTranslationOptions(WagtailTranslationOptions):
    fields = ()


translator.register(MultiFieldPanelPage, MultiFieldPanelTranslationOptions)
translator.register(MultiFieldPanelSnippet, MultiFieldPanelTranslationOptions)


class InlinePanelTranslationOptions(WagtailTranslationOptions):
    fields = ('field_name', 'image_chooser', 'fieldrow_name',)


translator.register(BaseInlineModel, InlinePanelTranslationOptions)


class InlinePanelTranslationOptions(WagtailTranslationOptions):
    fields = ()


translator.register(PageInlineModel, InlinePanelTranslationOptions)
translator.register(SnippetInlineModel, InlinePanelTranslationOptions)


@register(InlinePanelPage)
class InlinePanelModelTranslationOptions(WagtailTranslationOptions):
    fields = ()


translator.register(InlinePanelSnippet, InlinePanelModelTranslationOptions)
