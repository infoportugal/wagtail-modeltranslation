# coding utf-8

from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
try:
    from wagtail.core.models import Page
except ImportError:
    from wagtail.wagtailcore.models import Page

@register(Page)
class PageTR(TranslationOptions):
    fields = (
        'title',
        'slug',
        'seo_title',
        'search_description',
        'url_path',
    )
