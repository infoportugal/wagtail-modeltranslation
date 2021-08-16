.. _advanced settings:

Advanced Settings
=================

Besides the django-modeltranslation settings, documented `here <http://django-modeltranslation.readthedocs.io/en/latest/installation.html#advanced-settings>`_ this app provides the following custom settings:

``WAGTAILMODELTRANSLATION_CUSTOM_SIMPLE_PANELS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``[]`` (empty list)

This setting is used to add custom "simple panel" classes (all panels that contain directly a field value, like FieldPanel or ImageChooserPanel) that need patching but are not included by default, resulting in not being created translated versions of that panel in wagtail admin.
If, for example, you're using wagtail-embedvideos the EmbedVideoChooserPanel is not patched by default so you'd need to include the fully qualified class name like the example below. This setting must be a list of fully qualified class names as strings.

.. code-block:: python

    WAGTAILMODELTRANSLATION_CUSTOM_SIMPLE_PANELS = ['wagtail_embed_videos.edit_handlers.EmbedVideoChooserPanel']


``WAGTAILMODELTRANSLATION_CUSTOM_COMPOSED_PANELS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``[]`` (empty list)

This setting behaves as the above but should be used for panels that are composed by other panels (MultiFieldPanel or FieldRowPanel for example).

.. code-block:: python

    WAGTAILMODELTRANSLATION_CUSTOM_COMPOSED_PANELS = ['app_x.module_y.PanelZ']


``WAGTAILMODELTRANSLATION_TRANSLATE_SLUGS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

This setting makes slug and url_path localized. If True, each page will have a slug and url_path per language. If a slug field is not translated it will be automatically populated when the page title of it's language is filled.

.. code-block:: python

    WAGTAILMODELTRANSLATION_TRANSLATE_SLUGS = True


``WAGTAILMODELTRANSLATION_LOCALE_PICKER``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

This setting injects a locale picker in the editor interface, so that only selected locale fields are shown.

.. code-block:: python

    WAGTAILMODELTRANSLATION_LOCALE_PICKER = True


``WAGTAILMODELTRANSLATION_LOCALE_PICKER_DEFAULT``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

This setting specifies, which languages should initially be enabled on the edit pages when the locale picker is used. If not set, just the default language from ``MODELTRANSLATION_DEFAULT_LANGUAGE`` is initially enabled.

.. code-block:: python

    WAGTAILMODELTRANSLATION_LOCALE_PICKER_DEFAULT = None            # only default language initially enabled
    WAGTAILMODELTRANSLATION_LOCALE_PICKER_DEFAULT = [ ]             # all languages initially disabled
    WAGTAILMODELTRANSLATION_LOCALE_PICKER_DEFAULT = [ 'en', 'de' ]  # these languages initially enabled

``WAGTAILMODELTRANSLATION_LOCALE_PICKER_STORE``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

If set to true, the language picker will restore language selection on each page. Otherwise, the default will be used

.. code-block:: python

    WAGTAILMODELTRANSLATION_LOCALE_PICKER_RESTORE = False # the default will be used on each page
    WAGTAILMODELTRANSLATION_LOCALE_PICKER_RESTORE = True  # the last used language will be used on each page
