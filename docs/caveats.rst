.. _caveats:

Caveats
=======

Wagtail's ``Page`` patch
------------------------

``wagtail-modeltranslation`` patches Wagtail's ``Page`` model with translation fields
``title_xx``, ``slug_xx``, ``seo_title_xx``, ``search_description_xx`` and ``url_path_xx``
where "xx" represents the language code for each translated language. This is done without
migrations through :ref:`management_commands-sync_page_translation_fields`. Since
``Page`` model belongs to Wagtail it's within the realm of possibility that one day Wagtail
may add a conflicting field to ``Page`` thus interfering with ``wagtail-modeltranslation``.

See also :ref:`management_commands-makemigrations_translation` to better understand how
migrations are managed with ``wagtail-modeltranslation``.

Wagtail's slugurl
-----------------

Wagtail's ``slugurl`` tag does not work across languages. To work around this
``wagtail-modeltranslation`` provides a drop-in replacement tag named
:ref:`template tags-slugurl_trans` which by default takes the slug parameter in the
default language.

Replace any usages of Wagtail's ``{% slugurl 'default_lang_slug' %}`` for

.. code-block:: django

    {% load wagtail_modeltranslation %}
    ...
    {% slugurl_trans 'default_lang_slug' %}
