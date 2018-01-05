# coding: utf-8
from modeltranslation.translator import translator, register, TranslationOptions

from wagtail_modeltranslation.tests.models import TestRootPage, TestSlugPage1, TestSlugPage2, PatchTestPage, \
    PatchTestSnippet, FieldPanelPage, ImageChooserPanelPage, FieldRowPanelPage, MultiFieldPanelPage, InlinePanelPage, \
    FieldPanelSnippet, ImageChooserPanelSnippet, FieldRowPanelSnippet, MultiFieldPanelSnippet, PageInlineModel, \
    BaseInlineModel, StreamFieldPanelPage, StreamFieldPanelSnippet, SnippetInlineModel, InlinePanelSnippet, \
    TestSlugPage1Subclass, RoutablePageTest


# Wagtail Models

@register(TestRootPage)
class TestRootPagePageTranslationOptions(TranslationOptions):
    fields = ()


@register(TestSlugPage1)
class TestSlugPage1TranslationOptions(TranslationOptions):
    fields = ()


@register(TestSlugPage2)
class TestSlugPage2TranslationOptions(TranslationOptions):
    fields = ()


@register(TestSlugPage1Subclass)
class TestSlugPage1SubclassTranslationOptions(TranslationOptions):
    pass


@register(PatchTestPage)
class PatchTestPageTranslationOptions(TranslationOptions):
    fields = ('description',)


class PatchTestSnippetTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(PatchTestSnippet, PatchTestSnippetTranslationOptions)


# Panel Patching Models

class FieldPanelTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(FieldPanelPage, FieldPanelTranslationOptions)
translator.register(FieldPanelSnippet, FieldPanelTranslationOptions)


class ImageChooserPanelTranslationOptions(TranslationOptions):
    fields = ('image',)


translator.register(ImageChooserPanelPage, ImageChooserPanelTranslationOptions)
translator.register(ImageChooserPanelSnippet, ImageChooserPanelTranslationOptions)


class FieldRowPanelTranslationOptions(TranslationOptions):
    fields = ('other_name',)


translator.register(FieldRowPanelPage, FieldRowPanelTranslationOptions)
translator.register(FieldRowPanelSnippet, FieldRowPanelTranslationOptions)


class StreamFieldPanelTranslationOptions(TranslationOptions):
    fields = ('body',)


translator.register(StreamFieldPanelPage, StreamFieldPanelTranslationOptions)
translator.register(StreamFieldPanelSnippet, StreamFieldPanelTranslationOptions)


class MultiFieldPanelTranslationOptions(TranslationOptions):
    fields = ()


translator.register(MultiFieldPanelPage, MultiFieldPanelTranslationOptions)
translator.register(MultiFieldPanelSnippet, MultiFieldPanelTranslationOptions)


class InlinePanelTranslationOptions(TranslationOptions):
    fields = ('field_name', 'image_chooser', 'fieldrow_name',)


translator.register(BaseInlineModel, InlinePanelTranslationOptions)


class InlinePanelTranslationOptions(TranslationOptions):
    fields = ()


translator.register(PageInlineModel, InlinePanelTranslationOptions)
translator.register(SnippetInlineModel, InlinePanelTranslationOptions)


@register(InlinePanelPage)
class InlinePanelModelTranslationOptions(TranslationOptions):
    fields = ()


translator.register(InlinePanelSnippet, InlinePanelModelTranslationOptions)


@register(RoutablePageTest)
class RoutablePageTestTranslationOptions(TranslationOptions):
    fields = ()
