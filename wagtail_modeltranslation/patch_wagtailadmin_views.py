# -*- coding: utf-8 -*-

from django.conf import settings

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin import messages
from wagtail.wagtailadmin.views.pages import get_valid_next_url_from_request

from wagtail_modeltranslation.patch_wagtailadmin_forms import NewCopyForm

# Copied from wagtail.wagtailadmin.views.pages.copy and modified
def new_copy(request, page_id):
    page = Page.objects.get(id=page_id)

    # Parent page defaults to parent of source page
    parent_page = page.get_parent()

    # Check if the user has permission to publish subpages on the parent
    can_publish = parent_page.permissions_for_user(request.user).can_publish_subpage()

    # Create the form
    form = NewCopyForm(request.POST or None, page=page, can_publish=can_publish)

    next_url = get_valid_next_url_from_request(request)

    # Check if user is submitting
    if request.method == 'POST':
        # Prefill parent_page in case the form is invalid (as prepopulated value for the form field,
        # because ModelChoiceField seems to not fall back to the user given value)
        parent_page = Page.objects.get(id=request.POST['new_parent_page'])

        if form.is_valid():
            # Receive the parent page (this should never be empty)
            if form.cleaned_data['new_parent_page']:
                parent_page = form.cleaned_data['new_parent_page']

            # Make sure this user has permission to add subpages on the parent
            if not parent_page.permissions_for_user(request.user).can_add_subpage():
                raise PermissionDenied

            # Re-check if the user has permission to publish subpages on the new parent
            can_publish = parent_page.permissions_for_user(request.user).can_publish_subpage()

            update_attrs = {
                'title': form.cleaned_data['new_title'],
                'slug': form.cleaned_data['new_slug'],
            }
            
            for isocode, description in settings.LANGUAGES:
                for fieldname in ['title', 'slug']:
                    update_attrs['%s_%s' % (fieldname, isocode)] = form.cleaned_data['new_%s_%s' % (fieldname, isocode)]
                    
            # Copy the page
            new_page = page.copy(
                recursive=form.cleaned_data.get('copy_subpages'),
                to=parent_page,
                update_attrs=update_attrs,
                keep_live=(can_publish and form.cleaned_data.get('publish_copies')),
                user=request.user,
            )

            # Give a success message back to the user
            if form.cleaned_data.get('copy_subpages'):
                messages.success(
                    request,
                    _("Page '{0}' and {1} subpages copied.").format(page.title, new_page.get_descendants().count())
                )
            else:
                messages.success(request, _("Page '{0}' copied.").format(page.title))

            # Redirect to explore of parent page
            if next_url:
                return redirect(next_url)
            return redirect('wagtailadmin_explore', parent_page.id)

    return render(request, 'wagtailadmin/pages/copy.html', {
        'LANGUAGES': settings.LANGUAGES,
        'page': page,
        'form': form,
        'next': next_url,
    })