.. Wagtail ModelTranslation Documentation documentation master file, created by
   sphinx-quickstart on Tue Aug 18 11:42:59 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================
Wagtail Modeltranslation
========================

This app is built using core features of django-modeltranslation: https://github.com/deschler/django-modeltranslation

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
- Wagtail admin integration (for Page, BaseSetting and Snippet models)
- Flexible fallbacks, auto-population and more!
- Default Page model fields has translatable fields by default


Contents
========

.. toctree::
   :maxdepth: 2

   Introduction
   Installation
   Registering Models
   advanced settings
   template tags
   management commands
   recommended reading
   releases/index
   AUTHORS
   CHANGELOG
