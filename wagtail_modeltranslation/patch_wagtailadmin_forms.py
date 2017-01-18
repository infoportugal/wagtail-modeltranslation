# -*- coding: utf-8 -*-

from django.conf import settings

from django import forms

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.forms import WagtailAdminPageForm, CopyForm
from wagtail.wagtailcore.models import Page


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


# Copied from wagtail.wagtailadmin.forms.CopyForm and modified
# We here inherit the original CopyForm, we could define a new one instead (as at today we redefine all its methods)
class NewCopyForm(CopyForm):
    def __init__(self, *args, **kwargs):
        # CopyPage must be passed a 'page' kwarg indicating the page to be copied
        self.page = kwargs.pop('page').specific
        can_publish = kwargs.pop('can_publish')
        super(CopyForm, self).__init__(*args, **kwargs)  # Yeah, call CopyForm not NewCopyForm

        # self.fields['new_title'] = forms.CharField(initial=self.page.title, label=_("New title"))
        for isocode, description in settings.LANGUAGES:
            self.fields['new_title_%s' % isocode] = forms.CharField(initial=getattr(self.page, "title_%s" % isocode), label=_("New title") + (" [%s]" % isocode))

        # self.fields['new_slug'] = forms.SlugField(initial=self.page.slug, label=_("New slug"))
        for isocode, description in settings.LANGUAGES:
            self.fields['new_slug_%s' % isocode] = forms.CharField(initial=getattr(self.page, "slug_%s" % isocode), label=_("New slug") + (" [%s]" % isocode))

        self.fields['new_parent_page'] = forms.ModelChoiceField(
            initial=self.page.get_parent(),
            queryset=Page.objects.all(),
            widget=widgets.AdminPageChooser(can_choose_root=True),
            label=_("New parent page"),
            help_text=_("This copy will be a child of this given parent page.")
        )

        pages_to_copy = self.page.get_descendants(inclusive=True)
        subpage_count = pages_to_copy.count() - 1
        if subpage_count > 0:
            self.fields['copy_subpages'] = forms.BooleanField(
                required=False, initial=True, label=_("Copy subpages"),
                help_text=ungettext(
                    "This will copy %(count)s subpage.",
                    "This will copy %(count)s subpages.",
                    subpage_count) % {'count': subpage_count})

        if can_publish:
            pages_to_publish_count = pages_to_copy.live().count()
            if pages_to_publish_count > 0:
                # In the specific case that there are no subpages, customise the field label and help text
                if subpage_count == 0:
                    label = _("Publish copied page")
                    help_text = _("This page is live. Would you like to publish its copy as well?")
                else:
                    label = _("Publish copies")
                    help_text = ungettext(
                        "%(count)s of the pages being copied is live. Would you like to publish its copy?",
                        "%(count)s of the pages being copied are live. Would you like to publish their copies?",
                        pages_to_publish_count) % {'count': pages_to_publish_count}

                self.fields['publish_copies'] = forms.BooleanField(
                    required=False, initial=True, label=label, help_text=help_text
                )

    def clean(self):
        cleaned_data = super(CopyForm, self).clean()  # Yeah, call CopyForm not NewCopyForm

        # Make sure the slug isn't already in use
        # slug = cleaned_data.get('new_slug')

        # New parent page given in form or parent of source, if parent_page is empty
        parent_page = cleaned_data.get('new_parent_page') or self.page.get_parent()

        from wagtail_modeltranslation.patch_wagtailadmin import _validate_slugs

        slugs_to_check = {}
        for isocode, description in settings.LANGUAGES:
            formfieldname = 'new_slug_%s' % isocode
            slugs_to_check["slug_%s" % isocode] = cleaned_data.get(formfieldname) or ""

        for slugfield, des_error in _validate_slugs(self.page,
                                                    parent_page=parent_page,
                                                    slugs_to_check=slugs_to_check,
                                                    exclude_self=False).items():
            formfieldname = 'new_%s' % slugfield
            self._errors[formfieldname] = self.error_class(
                [_("This slug is already in use within the context of its parent page \"%s\"" % parent_page)]
            )
            # The slug is no longer valid, hence remove it from cleaned_data
            del cleaned_data[formfieldname]
            
        return cleaned_data
