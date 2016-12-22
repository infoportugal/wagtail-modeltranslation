# -*- coding: utf-8 -*-

from django.conf import settings

from django import forms
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin import widgets
from wagtail.wagtailadmin.forms import CopyForm
from wagtail.wagtailcore.models import Page

# Copied from wagtail.wagtailadmin.forms.CopyForm and modified
class NewCopyForm(CopyForm):
    def __init__(self, *args, **kwargs):
        # CopyPage must be passed a 'page' kwarg indicating the page to be copied
        self.page = kwargs.pop('page').specific
        can_publish = kwargs.pop('can_publish')
        super(CopyForm, self).__init__(*args, **kwargs)

        self.fields['new_title'] = forms.CharField(initial=self.page.title, label=_("New title"))
        for isocode, description in settings.LANGUAGES:
            self.fields['new_title_%s' % isocode] = forms.CharField(initial=getattr(self.page, "title_%s" % isocode), label=_("New title") + (" [%s]" % isocode))
            
        self.fields['new_slug'] = forms.SlugField(initial=self.page.slug, label=_("New slug"))
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
