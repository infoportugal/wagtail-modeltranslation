from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from wagtail.core.models import Page

from wagtail_modeltranslation import settings


@register(Page)
class PageTR(TranslationOptions):
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
