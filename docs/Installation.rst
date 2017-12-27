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
=====

To setup the application please follow these steps:

1. In the settings/base.py file:

   - Add wagtail_modeltranslation to the INSTALLED_APPS

    .. code-block:: console

        INSTALLED_APPS = (
         ...
        'wagtail_modeltranslation',
         )


    - Add django.middleware.locale.LocaleMiddleware to MIDDLEWARE_CLASSES.


    .. code-block:: console

       MIDDLEWARE_CLASSES = (
       ...

       'django.middleware.locale.LocaleMiddleware',
       )


    - Set ``USE_I18N = True``

..  _language_settings:

    - Configure your LANGUAGES.

      The LANGUAGES variable must contain all languages you will use for translation. The first language is treated as the
      *default language*.

      Modeltranslation uses the list of languages to add localized fields to the models registered for translation.
      For example, to use the languages Portuguese, Spanish and French in your project, set the LANGUAGES variable like this
      (where ``pt`` is the default language). In required fields the one for the default language is marked as required (for more advanced usage check `django-modeltranslation required_languages <http://django-modeltranslation.readthedocs.io/en/latest/registration.html#required-fields>`_.)

      .. code-block:: console

         LANGUAGES = (
            ('pt', u'Portugese'),
            ('es', u'Spanish'),
            ('fr', u'French'),
          )

.. warning::

   When the LANGUAGES setting isn't present in ``settings/base.py`` (and neither is ``MODELTRANSLATION_LANGUAGES``), it defaults to Django's  global LANGUAGES setting instead, and there are quite a few languages in the default!


2. Create a ``translation.py`` file in your app directory and register ``TranslationOptions`` for every model you want to translate.

.. code-block:: console

   from .models import foo
   from modeltranslation.translator import TranslationOptions
   from wagtail_modeltranslation.translation import register

   @register(foo)
   class FooTR(TranslationOptions):
       fields = (
          'body',
       )


3. Run ``python manage.py makemigrations`` followed by ``python manage.py migrate``. This will add extra fields in the database.


4. Define the panels for the original fields, as you normally would, as wagtail-modeltranslation will generate the panels for the translated fields.
