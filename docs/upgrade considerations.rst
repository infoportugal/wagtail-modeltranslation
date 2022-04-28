Upgrade considerations (v0.10.8)
================================

- Template tag ``change_lang`` now needs a second parameter, ``page``

Upgrade considerations (v0.8)
=============================

This version includes breaking changes as some key parts of the app have been
re-written:

- The most important change is that ``Page`` is now patched with translation
  fields.
- ``WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE`` setting has been
  deprecated.

To upgrade to this version you need to:

- Replace the ``WagtailTranslationOptions`` with ``TranslationOptions`` in all
  translation.py files
- Run :code:`python manage.py sync_page_translation_fields` at least once to
  create ``Page``'s translation fields
- Replace any usages of Wagtail's ``{% slugurl ... %}`` for
  :code:`wagtail-modeltranslation`'s own ``{% slugurl_trans ... %}``
- While optional it's recommended to add
  ``'wagtail_modeltranslation.makemigrations'`` to your INSTALLED_APPS. This
  will override Django's ``makemigrations`` command to avoid creating spurious
  ``Page`` migrations.

Upgrade considerations (v0.6)
=============================

This version has some important changes as there was a refactoring to include
django-modeltranslation as a dependency instead of duplicating their code in
our version. This allow us to focus on Wagtail admin integration features as
django-modeltranslation is very well mantained and is very quickly to fix
problems with the latest Django versions. This way we also keep all the
django-modeltranslation features (if you want you can also customize
django-admin, for example). We also provide a new class to create the
translation options classes: **WagtailTranslationOptions**
Most of the changes are related to imports as they change from
wagtail-modeltranslation to modeltranslation.

To upgrade to this version you need to:

- Replace the ``TranslationOptions`` with ``WagtailTranslationOptions`` in all
  translation.py files
- The import of the register decorator is now
  ``from modeltranslation.decorators import register``
- The import of translator is now
  ``from modeltranslation.translator import translator``
