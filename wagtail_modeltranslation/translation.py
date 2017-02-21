# coding utf-8

from modeltranslation.decorators import register
from wagtail.wagtailcore.models import Page

from wagtail_modeltranslation.translator import TranslationOptions


@register(Page)
class PageTR(TranslationOptions):
    pass
