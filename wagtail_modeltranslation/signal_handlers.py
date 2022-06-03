from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from modeltranslation import settings as mt_settings
from wagtail.core.models import Site


# Clear the wagtail_site_root_paths_XX from the cache whenever Site records are updated.
def post_save_site_signal_handler(instance, update_fields=None, **kwargs):
    for language in mt_settings.AVAILABLE_LANGUAGES:
        cache.delete('wagtail_site_root_paths_{}'.format(language))


def post_delete_site_signal_handler(instance, **kwargs):
    for language in mt_settings.AVAILABLE_LANGUAGES:
        cache.delete('wagtail_site_root_paths_{}'.format(language))


def register_signal_handlers():
    post_save.connect(post_save_site_signal_handler, sender=Site)
    post_delete.connect(post_delete_site_signal_handler, sender=Site)
