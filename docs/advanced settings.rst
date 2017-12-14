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


``WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.6.0

Default: ``None``

This setting enables consistency for the original (not translated) 'slug' value that is saved to the ``Page`` model table (wagtailcore_page). The value saved to the DB will be independent of user's current language and instead will rely on this setting's language.
This is specially useful when Wagtail pages are edited by users of different languages and the site makes use of `slugurl <http://docs.wagtail.io/en/latest/topics/writing_templates.html#slugurl>`_.

``None``
    [set by default]

    Setting turned off. Behaviour is the same as django-modeltranslation, meaning the value of the original slug field is undetermined (check `The State of the Original Field <http://django-modeltranslation.readthedocs.io/en/latest/usage.html#the-state-of-the-original-field>`_).

``'default'``
    Original slug field saved to the DB is in django-modeltranslation's default language.

``'xx'`` (language code)
    Use a language code to ensure the value saved to the original slug field is in the chosen language. For example: ``'en'``.

Example:

.. code-block:: python

    WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE = 'default'
