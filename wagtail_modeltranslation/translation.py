# coding utf-8

from wagtail.wagtailcore.models import Page
from wagtail_modeltranslation.translator import TranslationOptions
from wagtail_modeltranslation.decorators import register


@register(Page)
class PageTR(TranslationOptions):
    fields = (
        'title',
        'slug',
        'seo_title',
        'search_description',
        'url_path',)
