# coding: utf-8

import json

from django.utils.html import format_html, format_html_join
from django.conf import settings
from django.conf.urls import url
from django.http import QueryDict
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page


@hooks.register('insert_editor_js')
def translated_slugs():
    js_files = [
        'modeltranslation/js/wagtail_translated_slugs.js',
    ]

    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>', (
        (settings.STATIC_URL, filename) for filename in js_files)
    )

    lang_codes = []
    for lang in settings.LANGUAGES:
        lang_codes.append("'%s'" % lang[0])

    js_languages = "<script>var langs=[%s];</script>" % (", ".join(lang_codes))

    return format_html(js_languages) + js_includes


###############################################################################
# Copy StreamFields content
###############################################################################
@csrf_exempt
def return_translation_target_field_rendered_html(request, page_id):
    """
    Ajax view that allows to duplicate content
    between translated streamfields
    """

    page = Page.objects.get(pk=page_id)

    if request.is_ajax():
        origin_field_name = request.POST.get('origin_field_name')
        target_field_name = request.POST.get('target_field_name')
        related_model = request.POST.get('related_model')
        related_model_offset = int(request.POST.get('related_model_offset', 0) or 0)
        origin_field_serialized = json.loads(
            request.POST.get('serializedOriginField'))
        # Patch field prefixes from origin field to target field
        target_field_patched = []
        for item in origin_field_serialized:
            patched_item = None
            for att in item.iteritems():
                target_value = att[1]
                if att[0] == 'name':
                    target_value = att[1].replace(
                        origin_field_name, target_field_name)
                    patched_item = {"name": target_value}
                else:
                    patched_item["value"] = att[1]

            target_field_patched.append(patched_item)

        # convert to QueryDict
        q_data = QueryDict('', mutable=True)
        for item in target_field_patched:
            q_data.update({item['name']: item['value']})

        # get render html

        if related_model :
            target_field = getattr(page.specific, related_model).model._meta.get_field(target_field_name)
            q_data_target_field_name = "%s-%s-%s" % (related_model, related_model_offset, target_field_name)
        else :
            target_field = page.specific._meta.get_field(target_field_name)
            q_data_target_field_name = target_field_name

        value_data = target_field.stream_block.value_from_datadict(
            q_data, {}, q_data_target_field_name)
        target_field_content_html = target_field.formfield().widget.render(
            q_data_target_field_name, value_data)

    # return html json
    return HttpResponse(
        json.dumps(target_field_content_html), content_type='application/json')


@hooks.register('register_admin_urls')
def copy_streamfields_content():

    return [
        url(r'(?P<page_id>\d+)/edit/copy_translation_content$',
            return_translation_target_field_rendered_html, name=''),
    ]


@hooks.register('insert_editor_js')
def streamfields_translation_copy():
    """
    Includes script in editor html file that creates
    buttons to copy content between translated stream fields
    and send a ajax request to copy the content.
    """

    # includes the javascript file in the html file
    js_files = [
        'modeltranslation/js/copy_stream_fields.js',
    ]

    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>', (
        (settings.STATIC_URL, filename) for filename in js_files)
    )

    return js_includes


@hooks.register('insert_editor_css')
def modeltranslation_page_editor_css():
    return format_html('<link rel="stylesheet" href="' \
        + settings.STATIC_URL \
        + 'modeltranslation/css/page_editor_modeltranslation.css" >')
