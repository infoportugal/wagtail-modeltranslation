# coding: utf-8

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import translation
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from modeltranslation.utils import build_localized_fieldname
from wagtail.admin import widgets
from wagtail.admin.forms.pages import CopyForm
from wagtail.models import Page

from wagtail_modeltranslation import settings as wmt_settings


class PatchedCopyForm(CopyForm):
    def __init__(self, *args, **kwargs):
        # CopyPage must be passed a 'page' kwarg indicating the page to be copied
        self.page = kwargs.pop("page")
        self.user = kwargs.pop("user", None)
        can_publish = kwargs.pop("can_publish")
        super(CopyForm, self).__init__(*args, **kwargs)

        for code, name in settings.LANGUAGES:
            localized_fieldname = build_localized_fieldname("title", code)
            localized_field = Page._meta.get_field(localized_fieldname)
            locale_title = "new_{}".format(localized_fieldname)
            locale_label = "{} [{}]".format(_("New title"), code)
            self.fields[locale_title] = forms.CharField(
                initial=getattr(self.page, localized_fieldname),
                label=locale_label,
                required=not localized_field.blank,
            )

        allow_unicode = getattr(settings, "WAGTAIL_ALLOW_UNICODE_SLUGS", True)
        if wmt_settings.TRANSLATE_SLUGS:
            for code, name in settings.LANGUAGES:
                localized_fieldname = build_localized_fieldname("slug", code)
                localized_field = Page._meta.get_field(localized_fieldname)
                locale_title = "new_{}".format(localized_fieldname)
                locale_label = "{} [{}]".format(_("New slug"), code)
                self.fields[locale_title] = forms.SlugField(
                    initial=getattr(self.page, localized_fieldname),
                    label=locale_label,
                    required=not localized_field.blank,
                    allow_unicode=allow_unicode,
                    widget=widgets.SlugInput,
                )
        else:
            self.fields["new_slug"] = forms.SlugField(
                initial=self.page.slug, label=_("New slug")
            )

        self.fields["new_parent_page"] = forms.ModelChoiceField(
            initial=self.page.get_parent(),
            queryset=Page.objects.all(),
            widget=widgets.AdminPageChooser(can_choose_root=True, user_perms="copy_to"),
            label=_("New parent page"),
            help_text=_("This copy will be a child of this given parent page."),
        )
        pages_to_copy = self.page.get_descendants(inclusive=True)
        subpage_count = pages_to_copy.count() - 1
        if subpage_count > 0:
            self.fields["copy_subpages"] = forms.BooleanField(
                required=False,
                initial=True,
                label=_("Copy subpages"),
                help_text=ngettext(
                    "This will copy %(count)s subpage.",
                    "This will copy %(count)s subpages.",
                    subpage_count,
                )
                % {"count": subpage_count},
            )

        if can_publish:
            pages_to_publish_count = pages_to_copy.live().count()
            if pages_to_publish_count > 0:
                # In the specific case that there are no subpages, customise the field label and help text
                if subpage_count == 0:
                    label = _("Publish copied page")
                    help_text = _(
                        "This page is live. Would you like to publish its copy as well?"
                    )
                else:
                    label = _("Publish copies")
                    help_text = ngettext(
                        "%(count)s of the pages being copied is live. Would you like to publish its copy?",
                        "%(count)s of the pages being copied are live. Would you like to publish their copies?",
                        pages_to_publish_count,
                    ) % {"count": pages_to_publish_count}

                self.fields["publish_copies"] = forms.BooleanField(
                    required=False, initial=False, label=label, help_text=help_text
                )

            # Note that only users who can publish in the new parent page can create an alias.
            # This is because alias pages must always match their original page's state.
            self.fields["alias"] = forms.BooleanField(
                required=False,
                initial=False,
                label=_("Alias"),
                help_text=_("Keep the new pages updated with future changes"),
            )

    def clean(self):
        cleaned_data = super(CopyForm, self).clean()

        # Make sure the slug isn't already in use
        # slug = cleaned_data.get('new_slug')

        # New parent page given in form or parent of source, if parent_page is empty
        parent_page = cleaned_data.get("new_parent_page") or self.page.get_parent()

        # check if user is allowed to create a page at given location.
        if not parent_page.permissions_for_user(self.user).can_add_subpage():
            self._errors["new_parent_page"] = self.error_class(
                [
                    _('You do not have permission to copy to page "%(page_title)s"')
                    % {
                        "page_title": parent_page.specific_deferred.get_admin_display_title()
                    }
                ]
            )

        # Count the pages with the same slug within the context of our copy's parent page
        current_lang = get_language()
        slug_errors = {}
        for code, name in settings.LANGUAGES:
            locale_slug = "new_{}".format(build_localized_fieldname("slug", code))
            slug = cleaned_data.get(locale_slug)
            # we need to iterate over the children to get slugs because manager do not take in account the fallbacks
            activate(code)
            children_slugs = [child.slug for child in parent_page.get_children()]
            if slug and slug in children_slugs:
                self._errors[locale_slug] = self.error_class(
                    [
                        _('This slug is already in use within the context of its parent page "%(parent_page_title)s"')
                        % {"parent_page_title": parent_page}
                    ]
                )
        # back to current lang
        activate(current_lang)

        # Don't allow recursive copies into self
        if cleaned_data.get("copy_subpages") and (
            self.page == parent_page or parent_page.is_descendant_of(self.page)
        ):
            self._errors["new_parent_page"] = self.error_class(
                [_("You cannot copy a page into itself when copying subpages")]
            )

        return cleaned_data


def patch_admin_page_form(current_page_form):
    class WagtailFixedAdminPageForm(current_page_form):
        """
        Validate unicity of the slugs in every language. Take fallbacks into account.
        """

        def clean(self):
            cleaned_data = super().clean()

            # We follow the same logic as
            # `wagtail_modeltranslation.patch_wagtailadmin._validate_slugs`,
            # but we make sure that it work with new Page instances.

            siblings = self.parent_page.get_children()
            if self.instance.pk:
                siblings = siblings.not_page(self.instance)

            for code, name in settings.LANGUAGES:
                field_name = build_localized_fieldname("slug", code)
                slug_value = self.cleaned_data.get(field_name, None)
                if slug_value is None:
                    continue

                with translation.override(code):
                    siblings_slugs = [sibling.slug for sibling in siblings]
                    if slug_value in siblings_slugs:
                        self.add_error(
                            field_name,
                            forms.ValidationError(_("This slug is already in use")),
                        )

            return cleaned_data

    return WagtailFixedAdminPageForm
