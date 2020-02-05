# coding: utf-8

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

try:
    from wagtail.core.models import Page
    from wagtail.admin import widgets
    from wagtail.admin.forms.pages import CopyForm
except ImportError:
    from wagtail.wagtailcore.models import Page
    from wagtail.wagtailadmin import widgets
    from wagtail.wagtailadmin.forms import CopyForm


class PatchedCopyForm(CopyForm):
    def __init__(self, *args, **kwargs):
        # CopyPage must be passed a 'page' kwarg indicating the page to be copied
        self.page = kwargs.pop('page')
        self.user = kwargs.pop('user', None)
        can_publish = kwargs.pop('can_publish')
        super(CopyForm, self).__init__(*args, **kwargs)

        #self.fields['new_title'] = forms.CharField(initial=self.page.title, label=_("New title"))
        for code, name in settings.LANGUAGES:
            locale_title = "new_title_{}".format(code)
            locale_label = "{} [{}]".format(_("New title"), code)
            self.fields[locale_title] = forms.CharField(initial=self.page.title, label=locale_label)

        #self.fields['new_slug'] = forms.SlugField(initial=self.page.slug, label=_("New slug"))
        for code, name in settings.LANGUAGES:
            locale_title = "new_slug_{}".format(code)
            locale_label = "{} [{}]".format(_("New slug"), code)
            self.fields[locale_title] = forms.SlugField(initial=self.page.slug, label=locale_label)

        self.fields['new_parent_page'] = forms.ModelChoiceField(
            initial=self.page.get_parent(),
            queryset=Page.objects.all(),
            widget=widgets.AdminPageChooser(can_choose_root=True, user_perms='copy_to'),
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
        cleaned_data = super(CopyForm, self).clean()

        # Make sure the slug isn't already in use
        # slug = cleaned_data.get('new_slug')

        # New parent page given in form or parent of source, if parent_page is empty
        parent_page = cleaned_data.get('new_parent_page') or self.page.get_parent()

        # check if user is allowed to create a page at given location.
        if not parent_page.permissions_for_user(self.user).can_add_subpage():
            raise ValidationError({
                'new_parent_page': _("You do not have permission to copy to page \"%(page_title)s\"") % {'page_title': parent_page.get_admin_display_title()}
            })

        # Count the pages with the same slug within the context of our copy's parent page
        for code, name in settings.LANGUAGES:
            locale_slug = "new_slug_{}".format(code)
            slug = cleaned_data.get(locale_slug)

            param = 'slug_' + code
            query = {param: slug}
            if slug and parent_page.get_children().filter(**query).count():
                raise ValidationError({
                    locale_slug: _("This slug is already in use within the context of its parent page \"%s\"" % parent_page)
                })

        # Don't allow recursive copies into self
        if cleaned_data.get('copy_subpages') and (self.page == parent_page or parent_page.is_descendant_of(self.page)):
            raise ValidationError({
                'new_parent_page': _("You cannot copy a page into itself when copying subpages")
            })

        return cleaned_data
