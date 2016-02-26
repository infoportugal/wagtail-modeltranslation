from wagtail_modeltranslation.decorators import register
from wagtail_modeltranslation.translator import translator, TranslationOptions
from .models import News, TestPage


class NewsTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(News, NewsTranslationOptions)


@register(TestPage)
class TestPageTranslationOptions(TranslationOptions):
    fields = ('name',)
