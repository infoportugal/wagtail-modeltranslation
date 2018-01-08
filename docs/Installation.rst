.. _installation:

************
Installation
************

Requirements
============

* Wagtail >= 1.4



Installing using Pip
--------------------

..  code-block:: console

    $ pip install wagtail-modeltranslation


Installing using the source
---------------------------

*  From github: **git clone**  https://github.com/infoportugal/wagtail-modeltranslation.git

   * Copy wagtail_modeltranslation folder in project tree

   OR

* Download ZIP file on Github.com from infoportugal/wagtail-modeltranslation

   * Unzip and copy wagtail_modeltranslation folder in project tree


Quick Setup
===========

To setup the application please follow these steps:

1. In your settings file:

    - Add 'wagtail_modeltranslation' to ``INSTALLED_APPS``

        .. code-block:: console

            INSTALLED_APPS = (
                ...
                'wagtail_modeltranslation',
                'wagtail_modeltranslation.makemigrations',
            )

    - Add 'django.middleware.locale.LocaleMiddleware' to ``MIDDLEWARE`` (``MIDDLEWARE_CLASSES`` before django 1.10).

        .. code-block:: console

            MIDDLEWARE = (
                ...
                'django.middleware.locale.LocaleMiddleware',  # should be after SessionMiddleware and before CommonMiddleware
            )

    - Set ``USE_I18N = True``

..  _language_settings:

    - Configure your ``LANGUAGES`` setting.

        The ``LANGUAGES`` variable must contain all languages you will use for translation. The first language is treated as the *default language*.

        Modeltranslation uses the list of languages to add localized fields to the models registered for translation.
        For example, to use the languages Portuguese, Spanish and French in your project, set the ``LANGUAGES`` variable like this
        (where ``pt`` is the default language). In required fields the one for the default language is marked as required (for more advanced usage check `django-modeltranslation required_languages <http://django-modeltranslation.readthedocs.io/en/latest/registration.html#required-fields>`_.)

        .. code-block:: console
            from django.utils.translation import gettext_lazy as _

            LANGUAGES = (
                ('pt', _('Portuguese')),
                ('es', _('Spanish')),
                ('fr', _('French')),
            )

        .. warning::

           When the ``LANGUAGES`` setting isn't present in ``settings.py`` (and neither is ``MODELTRANSLATION_LANGUAGES``), it defaults to Django's  global LANGUAGES setting instead, and there are quite a few languages in the default!

    .. note::

        To learn more about preparing Wagtail for Internationalisation check the `Wagtail i18n docs <http://docs.wagtail.io/en/latest/advanced_topics/i18n/>`_.

2. Create a ``translation.py`` file in your app directory and register ``TranslationOptions`` for every model you want to translate.

    .. code-block:: console

       from .models import foo
       from modeltranslation.translator import TranslationOptions
       from modeltranslation.decorators import register

       @register(foo)
       class FooTR(TranslationOptions):
           fields = (
              'body',
           )

3. Run ``python manage.py makemigrations`` followed by ``python manage.py migrate``. This will add the tranlation fields to the database, repeat every time you add a new language or register a new model.

4. Run ``python manage.py sync_page_translation_fields``. This will add translation fields to Wagtail's ``Page`` table, repeat every time you add a new language.

5. If you're adding ``wagtail-modeltranslation`` to an existing site run ``python manage.py update_translation_fields``.

6. Define the panels for the original fields, as you normally would, as wagtail-modeltranslation will generate the panels for the translated fields.
