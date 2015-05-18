# WAGTAIL MODELTRANSLATION ADAPTATION

Simple app containing a mixin model that integrates modeltranslation
(https://github.com/deschler/django-modeltranslation) into wagtail panels system.

## Quick start

1. Add "wagtail_modeltranslation" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = (
            ...
            'wagtail_modeltranslation',
            **YOUR APPS**
        )

2. Use TranslationMixin to integrate django-modeltranslation with Wagtail admin:

        from wagtail_modeltranslation.models import TranslationMixin
        class FooModel(Page, TranslationMixin):
            foo = models.CharField()
        FooModel.panels = [...]

3. Visit django-modeltranslation for documentation - http://django-modeltranslation.readthedocs.org/en/latest/

## Release Notes:

### v0.0.3

- New methods;
- Now supports required fields;
- Fixed issue related to browser location;

### v0.0.2

**Features**:

- Prepopulated fields now works for translated fields (title and slug)
