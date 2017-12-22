# coding: utf-8

import re

from django import template
from django.core.urlresolvers import resolve
from django.utils.translation import activate, get_language

from six import iteritems

from wagtail.wagtailcore.models import Page

from modeltranslation.settings import DEFAULT_LANGUAGE

from wagtail_modeltranslation.contextlib import use_language

register = template.Library()


# TODO: check templatetag usage

# CHANGE LANGUAGE
@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    current_language = get_language()

    if 'request' in context and lang and current_language:
        request = context['request']
        match = resolve(request.path)
        non_prefixed_path = re.sub(current_language + '/', '', request.path, count=1)

        # means that is an wagtail page object
        if match.url_name == 'wagtail_serve':
            path_components = [component for component in non_prefixed_path.split('/') if component]
            page, args, kwargs = request.site.root_page.specific.route(request, path_components)

            activate(lang)
            translated_url = page.url
            activate(current_language)

            return translated_url
        elif match.url_name == 'wagtailsearch_search':
            path_components = [component for component in non_prefixed_path.split('/') if component]

            translated_url = '/' + lang + '/' + path_components[0] + '/'
            if request.GET:
                translated_url += '?'
                for key, value in iteritems(request.GET):
                    translated_url += key + '=' + value
            return translated_url

    return ''


# Alternative to slugurl which uses chosen or default language for language
@register.simple_tag(takes_context=True)
def slugurl_trans(context, slug, language=None):
    """
    Examples:
        {% slugurl_trans 'default_lang_slug' %}
        {% slugurl_trans 'de_lang_slug' 'de' %}

    Returns the URL for the page that has the given slug.
    """
    language = language or DEFAULT_LANGUAGE

    with use_language(language):
        page = Page.objects.filter(slug=slug).first()

    if page:
        return page.relative_url(context['request'].site)
    else:
        return None
