Wagtail Modeltranslation
========================

This app is built using core features of django-modeltranslation: https://github.com/deschler/django-modeltranslation

It's an alternative approach for i18n support on Wagtail CMS websites.

The wagtail-modeltranslation application is used to translate dynamic content of
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


Caveats
=======

:code:`wagtail-modeltranslation` patches Wagtail's :code:`Page` model with translation fields
:code:`title_xx`, :code:`slug_xx`, :code:`seo_title_xx`, :code:`search_description_xx` and :code:`url_path_xx` where "xx" represents the language code for each translated language. This
is done without migrations through command :code:`sync_page_translation_fields`. Since :code:`Page` model belongs to
Wagtail it's within the realm of possibility that one day Wagtail may add a conflicting field to :code:`Page` thus interfering with :code:`wagtail-modeltranslation`.

Wagtail's :code:`slugurl` tag does not work across languages. :code:`wagtail-modeltranslation` provides a drop-in replacement named :code:`slugurl_trans` which by default takes the slug parameter in the default language.

Quick start
===========

1. Install :code:`wagtail-modeltranslation`::

    pip install wagtail-modeltranslation

2. Add 'wagtail_modeltranslation' to your ``INSTALLED_APPS`` setting like this (before all apps that you want to translate)::

    INSTALLED_APPS = (
        ...
        'wagtail_modeltranslation',
        'wagtail_modeltranslation.makemigrations',
        'wagtail_modeltranslation.migrate',
    )

3. Add 'django.middleware.locale.LocaleMiddleware' to ``MIDDLEWARE`` on your ``settings.py``::

    MIDDLEWARE = (
        ...
        'django.middleware.locale.LocaleMiddleware',  # should be after SessionMiddleware and before CommonMiddleware
    )

4. Enable i18n on ``settings.py``::

    USE_I18N = True

5. Define available languages on ``settings.py``::

    from django.utils.translation import gettext_lazy as _

    LANGUAGES = (
        ('pt', _('Portuguese')),
        ('es', _('Spanish')),
        ('fr', _('French')),
    )

6. Create ``translation.py`` inside the root folder of the app where the model you want to translate exists::

    from .models import Foo
    from modeltranslation.translator import TranslationOptions
    from modeltranslation.decorators import register

    @register(Foo)
    class FooTR(TranslationOptions):
        fields = (
            'body',
        )

7. Run :code:`python manage.py makemigrations` followed by :code:`python manage.py migrate` (repeat every time you add a new language or register a new model)

8. Run :code:`python manage.py sync_page_translation_fields` (repeat every time you add a new language)

9. If you're adding :code:`wagtail-modeltranslation` to an existing site run :code:`python manage.py update_translation_fields`


Supported versions
==================

.. list-table:: Title
   :widths: 25 25 25 25
   :header-rows: 1

   * - wagtail-modeltranslation release
     - Compatible Wagtail versions
     - Compatible Django versions
     - Compatible Python versions
   * - 0.10
     - >= 1.12, < 2.12
     - >= 1.11
     - 2.7, 3.4, 3.5, 3.6
   * - 0.11
     - >= 2.13, < 3.0
     - >= 3.0
     - 3.6, 3.7, 3.8, 3.9
   * - 0.11
     - >= 3.0
     - >= 3.2
     - 3.7, 3.8, 3.9, 3.10

Upgrade considerations (v0.10.8)
================================

- Template tag ``change_lang`` now needs a second parameter, ``page``

Upgrade considerations (v0.8)
=============================

This version includes breaking changes as some key parts of the app have been re-written:

- The most important change is that ``Page`` is now patched with translation fields.
- ``WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE`` setting has been deprecated.

To upgrade to this version you need to:

- Replace the ``WagtailTranslationOptions`` with ``TranslationOptions`` in all translation.py files
- Run :code:`python manage.py sync_page_translation_fields` at least once to create ``Page``'s translation fields
- Replace any usages of Wagtail's ``{% slugurl ... %}`` for :code:`wagtail-modeltranslation`'s own ``{% slugurl_trans ... %}``
- While optional it's recommended to add ``'wagtail_modeltranslation.makemigrations'`` to your INSTALLED_APPS. This will override Django's ``makemigrations`` command to avoid creating spurious ``Page`` migrations.

Upgrade considerations (v0.6)
=============================

This version has some important changes as there was a refactoring to include django-modeltranslation as a dependency instead of
duplicating their code in our version. This allow us to focus on Wagtail admin integration features as django-modeltranslation is
very well mantained and is very quickly to fix problems with the latest Django versions. This way we also keep all the django-modeltranslation
features (if you want you can also customize django-admin, for example). We also provide a new class to create the translation options classes: **WagtailTranslationOptions**
Most of the changes are related to imports as they change from wagtail-modeltranslation to modeltranslation.

To upgrade to this version you need to:

- Replace the ``TranslationOptions`` with ``WagtailTranslationOptions`` in all translation.py files
- The import of the register decorator is now ``from modeltranslation.decorators import register``
- The import of translator is now ``from modeltranslation.translator import translator``


Project Home
------------
https://github.com/infoportugal/wagtail-modeltranslation

Documentation
-------------
http://wagtail-modeltranslation.readthedocs.io/
