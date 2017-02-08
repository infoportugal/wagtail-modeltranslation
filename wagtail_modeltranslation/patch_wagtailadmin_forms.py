# -*- coding: utf-8 -*-

from django.conf import settings

from django import forms

from wagtail.wagtailadmin.forms import WagtailAdminPageForm


class WagtailModeltranslationAdminPageForm(WagtailAdminPageForm):

    def __init__(self, data=None, files=None, parent_page=None, *args, **kwargs):
        super(WagtailModeltranslationAdminPageForm, self).__init__(data, files, parent_page, *args, **kwargs)

    def clean(self):

        cleaned_data = super(WagtailModeltranslationAdminPageForm, self).clean()

        from wagtail_modeltranslation.patch_wagtailadmin import _validate_slugs

        slugs_to_check = {}
        for isocode, description in settings.LANGUAGES:
            slugs_to_check["slug_%s" % isocode] = cleaned_data["slug_%s" % isocode]

        for slugfield, des_error in _validate_slugs(self.instance,
                                                    parent_page=self.parent_page,
                                                    slugs_to_check=slugs_to_check).items():
            self.add_error(slugfield, forms.ValidationError(des_error))

        return cleaned_data
