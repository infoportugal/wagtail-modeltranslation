# coding: utf-8

from django.utils.html import format_html, format_html_join
from django.conf import settings

from wagtail.wagtailcore import hooks


@hooks.register('insert_editor_js')
def translated_slugs():
    js_files = [
        'modeltranslation/js/wagtail_translated_slugs.js',
    ]

    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )

    lang_codes = []
    for lang in settings.LANGUAGES:
        lang_codes.append("'%s'" % lang[0])

    js_languages = "<script>var langs=[%s];</script>" % (", ".join(lang_codes))

    return format_html(js_languages) + js_includes
