.. _Registering Models:

Registering models for translation
==================================

``Modeltranslation`` can translate model fields of any model class.

In wagtail-modeltranslation a **TranslationMixin** is used with the Page model:

.. code-block::console

    from wagtail_modeltranslation.models import TranslationMixin

    class FooModel(TranslationMixin, Page):
       body = StreamField(...)


Registering models and their fields used for translation requires the following steps:

1. Create **translation.py** in your app directory.
2. Define the models you want to use, import wagtail-modeltranslation's **TranslationOptions** and the **register** decorator
3. Create a translation option class for every model you want to translate and precede the class with the **@register** decorator.

The wagtail-modeltranslation application reads the **translation.py** file in your app directory thereby triggering the registration
of the translation options found in the file.

A translation option is a class that declares which model fields are needed for translation. The class must derive from
**wagtail_modeltranslation.translator.TranslationOptions** and it must provide a **field** attribute storing the list of
field names. The option class must be registered with the **wagtail_modeltranslation.decorators.register** instance.

To illustrate this let's have a look at a simple example using a **Foo** model. The example only contains an **introduction**
and a **body** field.

Instead of a **Foo** model, this could be any Wagtail model class:

.. code-block:: console

   from .models import Foo
   from wagtail_modeltranslation.translation import TranslationOptions
   from wagtail_modeltranslation.decorators import register

   @register(Foo)
   class FooTR(TranslationOptions):
       fields = (
           'introduction',
           'body',
       )

In the above example, the **introduction** and **body** language fields will be be added for each language defined in
LANGUAGES in the settings file ,**base.py**, when the database is updated with **./manage.py makemigrations** and
**./manage.py migrate.**


At this point you are mostly done and the model classes registered for translation will have been added some auto-magical
fields. The next section explains how things are working under the hood.


Changes automatically applied to the model class
----------------------------------------------------

After registering the **Foo** model for translation a SQL dump of the Foo app will look like this:

.. code-block:: console

    $ ./manage.py sqlall news
    BEGIN;
    CREATE TABLE `news_Foo` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `introduction` varchar(255) NOT NULL,
        `introduction_pt` varchar(255) NULL,
        `introduction_es` varchar(255) NULL,
        `introduction_fr` varchar(255) NULL,
        `body` varchar(255) NOT NULL,
        `body_pt` varchar(255) NULL,
        `body_es` varchar(255) NULL,
        `body_fr` varchar(255) NULL,
    )
    ;
    CREATE INDEX `news_Foo_page_id` ON `news_Foo` (`page_id`);
    COMMIT;

Note the ``introduction_pt``, ``introduction_es``, ``introduction_fr``, ``body_pt``, ``body_es`` and ``body_fr`` fields
which are not declared in the original ``Foo`` model class have been added by the modeltranslation app. These are called
*translation fields*. There will be one for every language in your project's ``settings.py``.

The name of these additional fields is build using the original name of the translated field and appending one of the
language identifiers found in the ``settings.LANGUAGES``.

As these fields are added to the registered model class as fully valid Django model fields, they will appear in the db schema
for the model although it has not been specified on the model explicitly.


.. _register-precautions:

Precautions regarding registration approach
-------------------------------------------

Be aware that registration approach (as opposed to base-class approach) to models translation has a few caveats, though
(despite many pros).

First important thing to note is the fact that translatable models are being patched - that means their fields list is not
final until the modeltranslation code executes. In normal circumstances it shouldn't affect anything - as long as
``models.py`` contain only models' related code.

For example: consider a project where a ``ModelForm`` is declared in ``models.py`` just after its model. When the file is
executed, the form gets prepared - but it will be frozen with old fields list (without translation fields). That's because the
``ModelForm`` will be created before modeltranslation would add new fields to the model (``ModelForm`` gathers fields info at
class creation time, not instantiation time). Proper solution is to define the form in ``forms.py``, which wouldn't be imported
alongside with **models.py** (and rather imported from views file or urlconf).

Generally, for seamless integration with modeltranslation (and as sensible design anyway), the models.py`` should contain
 only bare models and model related logic.

.. _db-fields:

Committing fields to database
-----------------------------

.. _migrations:

Modeltranslation supports the migration system introduced by Django 1.7. Besides the normal workflow as described in Django's
`Migration Docs <https://docs.djangoproject.com/en/1.8/topics/migrations/>`__, you should do a migration whenever one of the following changes have been made to your project:

- Added or removed a language through ``settings.LANGUAGES`` or   ``settings.MODELTRANSLATION LANGUAGES``.
- Registered or unregistered a field through ``TranslationOptions``.

It doesn't matter if you are starting a fresh project or change an existing one, it's always:

1. ``python manage.py makemigration`` to create a new migration with
   the added or removed fields.

2. ``python manage.py migrate`` to apply the changes.


.. _required_langs:

Required fields
---------------

By default, all translation fields are optional (not required). This can be changed using a special attribute on
``TranslationOptions``::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('introduction', 'body',)
        required_languages = ('pt', 'es')

It's quite self-explanatory: for Portuguese and Spanish, the ``introduction`` and ``body`` translation fields are required. For other
languages, they are optional.

A more fine-grained control is available::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('introduction', 'body',)
        required_languages = {'pt': ('introduction', 'body'), 'default': ('introduction',)}

For Portuguese, all fields (both ``introduction`` and ``body``) are required; for all other languages, only
``introduction`` is required. The ``default`` is optional.

.. note::
    Requirement is enforced by ``blank=False``. Please remember that it will trigger validation only
    in modelforms and admin (as always in Django). Manual model validation can be performed via
    the ``full_clean()`` model method.

    The required fields are still ``null=True``, though.


.. _supported_field_matrix:

Matrix of supported fields
--------------------------

While the main purpose of modeltranslation is to translate text-like fields, translating other fields can be useful in
several situations. The table lists all model fields available in Django and Wagtail and gives an overview about their
current support status.

===============================  ===============
 Model Field                     Implemented
===============================  ===============
**AutoField**                           |n|
**BigIntegerField**                     |i|
**BooleanField**                        |y|
**CharField**                           |y|
**CommaSeparatedIntegerField**          |y|
**DateField**                           |y|
**DateTimeField**                       |y|
**DecimalField**                        |y|
**EmailField**                          |i|
**FileField**                           |y|
**FilePathField**                       |i|
**FloatField**                          |y|
**ImageField**                          |y|
**IntegerField**                        |y|
**IPAddressField**                      |y|
**GenericIPAddressField**               |y|
**NullBooleanField**                    |y|
**PositiveIntegerField**                |i|
**PositiveSmallIntegerField**           |i|
**SlugField**                           |i|
**SmallIntegerField**                   |i|
**StreamField**                         |y|
**TextField**                           |y|
**TimeField**                           |y|
**URLField**                            |i|
**ForeignKey**                          |y|
**OneToOneField**                       |y|
**ManyToManyField**                     |n|
===============================  ===============

.. |y| replace:: Yes
.. |i| replace:: Yes\*
.. |n| replace:: No
.. |u| replace:: ?

\* Implicitly supported (as subclass of a supported field)
