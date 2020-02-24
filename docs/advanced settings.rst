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

This setting makes slug and url_path localized. If True, each page will have a slug and url_path per language.

.. code-block:: python

    WAGTAILMODELTRANSLATION_TRANSLATE_SLUGS = True


``WAGTAILMODELTRANSLATION_LOCALE_PICKER``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

This setting injects a locale picker in the editor interface, so that only selected locale fields are shown.

.. code-block:: python

    WAGTAILMODELTRANSLATION_LOCALE_PICKER = True
