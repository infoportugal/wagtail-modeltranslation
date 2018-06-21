# coding utf-8

from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from wagtail_modeltranslation import settings
try:
    from wagtail.core.models import Page
except ImportError:
    from wagtail.wagtailcore.models import Page


fields = (
    'title',
    'seo_title',
    'search_description',
)
if settings.TRANSLATE_SLUGS:
    fields += (
        'slug',
        'url_path',
    )


@register(Page)
class PageTR(TranslationOptions):
    fields = fields
