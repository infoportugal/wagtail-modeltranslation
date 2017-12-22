from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.templatetags import wagtailcore_tags

from modeltranslation.settings import DEFAULT_LANGUAGE

from .contextlib import set_language


# decorate MigrationAutodetector.changes so we can silently remove wagtailcore changes
def slugurl_decorator(func):
    def wrapper(context, slug):
        with set_language(DEFAULT_LANGUAGE):
            page = Page.objects.filter(slug=slug).first()

        if page:
            return page.relative_url(context['request'].site)
        else:
            # default to original function
            return func(context, slug)

    return wrapper


def patch_wagtail_tags():
    # decorate slugurl tag so `{% slugurl 'default_lang_slug' %}` always works with original slug
    wagtailcore_tags.slugurl = slugurl_decorator(wagtailcore_tags.slugurl)
