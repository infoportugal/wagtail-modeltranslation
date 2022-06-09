from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailModeltranslationTestsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'wagtail_modeltranslation.tests'
    label = 'tests'
    verbose_name = _("Wagtail tests")
