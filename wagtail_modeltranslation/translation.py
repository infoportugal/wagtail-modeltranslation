# coding: utf-8

from wagtail.wagtailcore.models import Page

from modeltranslation.translator import translator, TranslationOptions


# regist wagtail Page model for translation
class PageTR(TranslationOptions):
    fields = ('title', 'slug')

translator.register(Page, PageTR)
