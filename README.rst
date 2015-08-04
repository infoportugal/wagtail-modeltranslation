================
Wagtail Modeltranslation
================

This app is based on django-modeltranslation: https://github.com/deschler/django-modeltranslation

It's an alternative approach for inexistent support to i18n on Wagtail CMS websites.

The modeltranslation application is used to translate dynamic content of
existing Wagtail CMS models to an arbitrary number of languages without having to
change the original model classes. It uses a registration approach (comparable
to Django's admin app) to be able to add translations to existing or new
projects and is fully integrated into the Django admin backend.

The advantage of a registration approach is the ability to add translations to
models on a per-app basis. You can use the same app in different projects,
may they use translations or not, and you never have to touch the original
model class.


.. image:: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true
    :target: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true


Features
========

- Add translations without changing existing models or views
- Translation fields are stored in the same table (no expensive joins)
- Supports inherited models (abstract and multi-table inheritance)
- Handle more than just text fields
- Wagtail CMS admin integration
- Flexible fallbacks, auto-population and more!
- Default Page model fields has translatable fields by default
- StreamFields are now supported!


Quick start
-----------

1. Add "wagtail_modeltranslation" to your INSTALLED_APPS setting like this (before all apps that you pretend to translate)::

    INSTALLED_APPS = (
        ...
        'wagtail_modeltranslation',
    )

2. Add "django.middleware.locale.LocaleMiddleware" to MIDDLEWARE_CLASSES on your settings.py:

    MIDDLEWARE_CLASSES = (
        ...
        'django.middleware.locale.LocaleMiddleware',
    )

3. Enable i18n on settings.py:

    USE_I18N = True

4. Define available languages on settings.py:

    LANGUAGES = (
        ('pt', u'Português'),
        ('es', u'Espanhol'),
        ('fr', u'Francês'),
    )

5. Create translation.py inside root folder of app where model you pretend to tranlslate exists:

    from .models import Foo
    from wagtail_modeltranslation.translator import TranslationOptions
    from wagtail_modeltranslation.decorators import register


    @register(Foo)
    class FooTR(TranslationOptions):
        fields = (
            'body',
        )

6. Add TranslationMixin to translatable model:

    class FooModel(TranslationMixin, Page):
        body = StreamField(...)

7. Run "./manage.py makemigrations" followed by "./manage.py migrate"



Project Home
------------
https://github.com/infoportugal/wagtail-modeltranslation

Documentation
-------------
soon available
