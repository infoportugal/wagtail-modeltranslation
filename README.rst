================
Wagtail Modeltranslation
================

This app is based on django-modeltranslation: https://github.com/deschler/django-modeltranslation

It's an alternative approach for i18n support on Wagtail CMS websites.

The modeltranslation application is used to translate dynamic content of
existing Wagtail models to an arbitrary number of languages, without having to
change the original model classes. It uses a registration approach (comparable
to Django's admin app) to add translations to existing or new projects and is
fully integrated into the Wagtail admin UI.

The advantage of a registration approach is the ability to add translations to
models on a per-app basis. You can use the same app in different projects,
whether or not they use translations, and without touching the original
model class.


.. image:: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true
    :target: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true


Features
========

- Add translations without changing existing models or views
- Translation fields are stored in the same table (no expensive joins)
- Supports inherited models (abstract and multi-table inheritance)
- Handle more than just text fields
- Wagtail admin integration
- Flexible fallbacks, auto-population and more!
- Default Page model fields has translatable fields by default
- StreamFields are now supported!


Upgrade from 0.2.x to v0.3
==========================
On v0.3 we did fix migration issues. Now, Page class translated fields (like title_<lang> or url_path_<lang>) are in child classes tables. (thanks nulopes!)

In order to migrate from v0.2.x to v0.3:

1. Delete wagtailcore_page modeltranslation related columns (replace field names suffix to your languages). Example::

    ALTER TABLE wagtailcore_page DROP COLUMN search_description_en, DROP COLUMN search_description_es, DROP COLUMN search_description_fr, DROP COLUMN search_description_pt;
    ALTER TABLE wagtailcore_page DROP COLUMN title_en, DROP COLUMN title_es, DROP COLUMN title_fr, DROP COLUMN title_pt;
    ALTER TABLE wagtailcore_page DROP COLUMN slug_en, DROP COLUMN slug_es, DROP COLUMN slug_fr, DROP COLUMN slug_pt;
    ALTER TABLE wagtailcore_page DROP COLUMN seo_title_en, DROP COLUMN seo_title_es, DROP COLUMN seo_title_fr, DROP COLUMN seo_title_pt;
    ALTER TABLE wagtailcore_page DROP COLUMN url_path_en, DROP COLUMN url_path_es, DROP COLUMN url_path_fr, DROP COLUMN url_path_pt;

2. Delete modeltranslation related migrations from wagtailcore migrations directory (virtualenv path: virtualenv/lib/python2.7/site-packages/wagtail/wagtailcore). **Important**: check if any of your apps migrations depends on this migration.

3. Delete migration row on table django_migrations;

5. python manage.py makemigrations;

4. python manage.py migrate;

5. python manage.py update_translation_fields;

6. python manage.py set_translation_url_paths;


Quick start
===========

1. Install :code:`wagtail-modeltranslation`::

    pip install wagtail-modeltranslation

2. Add "wagtail_modeltranslation" to your INSTALLED_APPS setting like this (before all apps that you want to translate)::

    INSTALLED_APPS = (
        ...
        'wagtail_modeltranslation',
    )

3. Add "django.middleware.locale.LocaleMiddleware" to MIDDLEWARE_CLASSES on your settings.py::

    MIDDLEWARE_CLASSES = (
        ...
        'django.middleware.locale.LocaleMiddleware',
    )

4. Enable i18n on settings.py::

    USE_I18N = True

5. Define available languages on settings.py::

    LANGUAGES = (
        ('pt', u'Português'),
        ('es', u'Espanhol'),
        ('fr', u'Francês'),
    )

6. Create translation.py inside the root folder of the app where the model you want to translate exists::

    from .models import Foo
    from wagtail_modeltranslation.translation import TranslationOptions
    from wagtail_modeltranslation.decorators import register


    @register(Foo)
    class FooTR(TranslationOptions):
        fields = (
            'body',
        )

7. Add :code:`TranslationMixin` to your translatable page or 'SnippetsTranslationMixin' for snippets::

    from wagtail_modeltranslation.models import TranslationMixin

    class FooModel(TranslationMixin, Page):
        body = StreamField(...)

8. Run :code:`python manage.py makemigrations` followed by :code:`python manage.py migrate`


Project Home
------------
https://github.com/infoportugal/wagtail-modeltranslation

Documentation
-------------
http://wagtail-modeltranslation-docs.readthedocs.org/en/latest/#
