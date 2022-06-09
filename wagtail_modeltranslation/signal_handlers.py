from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from modeltranslation import settings as mt_settings
from wagtail.core.models import Site
from wagtail.core.signals import post_page_move


# Clear the wagtail_site_root_paths_XX from the cache whenever Site records are updated.
def post_save_site_signal_handler(instance, update_fields=None, **kwargs):
    for language in mt_settings.AVAILABLE_LANGUAGES:
        cache.delete('wagtail_site_root_paths_{}'.format(language))


def post_delete_site_signal_handler(instance, **kwargs):
    for language in mt_settings.AVAILABLE_LANGUAGES:
        cache.delete('wagtail_site_root_paths_{}'.format(language))


# with this approach, we are doing multiple saves on object
# first on the move method that only updates this page's url_path and descendentes for current lang
# second, if we detect a move here, we force a new set_url_path and save on the reloaded instance from DB
def post_moved_handler(sender, **kwargs):
    if kwargs['url_path_before'] == kwargs['url_path_after']:
        # No URLs are changing :) nothing to do here!
        return

    kwargs['instance'].set_url_path(kwargs['parent_page_after'])
    kwargs['instance'].save()


def register_signal_handlers():
    post_save.connect(post_save_site_signal_handler, sender=Site)
    post_delete.connect(post_delete_site_signal_handler, sender=Site)

    post_page_move.connect(post_moved_handler)
