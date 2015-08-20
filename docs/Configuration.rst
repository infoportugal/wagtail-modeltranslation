*********************************
Configuration of Modeltranslation
*********************************


Modeltranslation also has some advanced settings to customize its behaviour.

.. _settings-modeltranslation_default_language:


Default language
----------------

``MODELTRANSLATION_DEFAULT_LANGUAGE``

Default: ``None``

To override the default language as described in :ref:`Configuration settings<language_settings>`, you can define a language in
``MODELTRANSLATION_DEFAULT_LANGUAGE``. Note that the value has to be in ``settings.LANGUAGES``, otherwise an
ImproperlyConfigured exception will be raised.

Example::

    MODELTRANSLATION_DEFAULT_LANGUAGE = 'pt'



Default languages
-----------------

``MODELTRANSLATION_LANGUAGES``

Default: same as LANGUAGES

Allows to set the languages the content will be translated into. If not set, by default all languages listed in LANGUAGES
will be used.

Example::

    LANGUAGES = (
        ('pt', 'Portuguese'),
        ('es', 'Spanish'),
        ('fr', 'French'),
    )

    MODELTRANSLATION_LANGUAGES = ('pt', 'es')

.. note::
    This setting may become useful if your users will be producing content for a restricted set of languages, while your
    application is translated into a greater number of locales.


.. _MODELTRANSLATION_FALLBACK_LANGUAGES:


Fallback languages
------------------

``MODELTRANSLATION_FALLBACK_LANGUAGES``

Default: ``(DEFAULT_LANGUAGE)``

By default modeltranslation will fallback to the computed value of the DEFAULT_LANGUAGE. This is either the first language
found in the LANGUAGES setting or the value defined through MODELTRANSLATION_DEFAULT_LANGUAGE which acts as an override.

This setting allows for a more fine grained tuning of the fallback behaviour by taking additional languages into account.
The language order is defined as a tuple or list of language codes.

Example::

    MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt', 'es')

Using a dict syntax it is also possible to define fallbacks by language. A default key is required in this case to define
the default behaviour of unlisted languages.

Example::

    MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('pt', 'es'), 'fr': ('pt',)}

.. note::
    Each language has to be in the LANGUAGES setting, otherwise an ``Improperly Configured`` exception is raised.


.. _settings-modeltranslation_prepopulate_language:


Prepopulate language
--------------------

``MODELTRANSLATION_PREPOPULATE_LANGUAGE``

Default: ``current active language``

By default modeltranslation will use the current request language for prepopulating admin fields specified in the
``prepopulated_fields`` admin property. This is often used to automatically fill slug fields.

This setting allows you to pin this functionality to a specific language.

Example::

    MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'fr'

.. note::
    The language has to be in the LANGUAGES setting, otherwise an ImproperlyConfigured exception is raised.


Translation files
-----------------

``MODELTRANSLATION_TRANSLATION_FILES``

Default: ``()`` (empty tuple)

Modeltranslation uses an autoregister feature similiar to the one in Django's admin. The autoregistration process will look
for a ``translation.py`` file in the root directory of each application that is in INSTALLED_APPS.

The setting ``MODELTRANSLATION_TRANSLATION_FILES`` is provided to extend the modules that are taken into account.

Syntax::

    MODELTRANSLATION_TRANSLATION_FILES = (
        '<APP1_MODULE>.translation',
        '<APP2_MODULE>.translation',
    )

Example::

    MODELTRANSLATION_TRANSLATION_FILES = (
        'foo.translation',
        'projects.translation',
    )


Custom fields
-------------

``MODELTRANSLATION_CUSTOM_FIELDS``

Default: ``()`` (empty tuple)


Modeltranslation supports the fields listed in the `Matrix of supported_fields`. In most cases subclasses of the supported
fields will work fine, too. Unsupported fields will throw an ``Improperly Configured`` exception.

The list of supported fields can be extended by defining a tuple of field names in your ``settings file``.

Example::

    MODELTRANSLATION_CUSTOM_FIELDS = ('MyField', 'MyOtherField',)

.. warning::
    This just prevents modeltranslation from throwing an ``Improperly Configured`` exception. Any unsupported field will
    most likely fail in one way or another. The feature is considered experimental and might be replaced by a more
    sophisticated mechanism in future versions.


.. _settings-modeltranslation_auto_populate:


Auto populate
-------------

``MODELTRANSLATION_AUTO_POPULATE``

Default: ``False``

This setting controls if the `multilingual_manager` should automatically populate language field values in its ``create``
and ``get_or_create`` method, and in model constructors, so that these two blocks of statements can be considered equivalent::

    foo.objects.populate(True).create(title='-- no translation yet --')
    with auto_populate(True):
        q = foo(title='-- no translation yet --')

    # same effect with MODELTRANSLATION_AUTO_POPULATE == True:

    foo.objects.create(title='-- no translation yet --')
    q = foo(title='-- no translation yet --')


Debug
-----

``MODELTRANSLATION_DEBUG``


Default: ``False``

Used for modeltranslation related debug output. Currently setting it to ``False`` will just prevent Django's development
server from printing the ``Registered xx models for translation`` message to stdout.


Fallbacks
---------

``MODELTRANSLATION_ENABLE_FALLBACKS``

Default: ``True``

Controls if fallback (both language and value) will occur.


.. _settings-modeltranslation_loaddata_retain_locale:


Retain locale
-------------

``MODELTRANSLATION_LOADDATA_RETAIN_LOCALE``

Default: ``True``

Control if the ``loaddata`` command should leave the settings-defined locale alone. Setting it to ``False`` will result in
previous behaviour of loaddata: inserting fixtures to database under en-us locale.
