.. _Registering Models:

Registering models for translation
==================================

``Modeltranslation`` can translate model fields of any model class.


Registering models and their fields used for translation requires the following steps:

1. Create **translation.py** in your app directory.
2. Define the models you want to use, import wagtail-modeltranslation's **WagtailTranslationOptions** and the django-modeltranslation **register** decorator
3. Create a translation option class for every model you want to translate and precede the class with the **@register** decorator.

The django-modeltranslation application reads the **translation.py** file in your app directory thereby triggering the registration
of the translation options found in the file.

A translation option is a class that declares which model fields are needed for translation. The class must derive from
**wagtail_modeltranslation.translator.WagtailTranslationOptions** and it must provide a **field** attribute storing the list of
field names. The option class must be registered with the **modeltranslation.decorators.register** instance.

To illustrate this let's have a look at a simple example using a **Foo** model. The example only contains an **introduction**
and a **body** field.

Instead of a **Foo** model, this could be any Wagtail model class:

.. code-block:: console

   from .models import Foo
   from wagtail_modeltranslation.translation import WagtailTranslationOptions
   from modeltranslation.decorators import register

   @register(Foo)
   class FooTR(WagtailTranslationOptions):
       fields = (
           'introduction',
           'body',
       )

In the above example, the **introduction** and **body** language fields will be be added for each language defined in
LANGUAGES in the settings file , **base.py**, when the database is updated with **./manage.py makemigrations** and
**./manage.py migrate.**


At this point you are mostly done and the model classes registered for translation will have been added some auto-magical
fields. For more under-the-hood details check `django-modeltranslation docs <http://django-modeltranslation.readthedocs.io/en/latest/registration.html>`_.

Now you can define the panels for the model as you normally would and wagtail-modeltranslation will take care of the creation of the panels for all the
supported languages.

.. code-block:: console

    # Indicate fields to include in Wagtail admin panel(s)
    Foo.content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('introduction', classname="full"),
        FieldPanel('body', classname="full"),
        ]
    #or with a custom edit_handler
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(sidebar_content_panels, heading='Sidebar content'),
        ObjectList(Page.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
    ])

The panel creation is available for **Page**, **BaseSetting** and **Snippet** models.

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

Generally, for seamless integration with modeltranslation (and as sensible design anyway), the models.py ``should contain only bare models and model related logic``.

.. _db-fields:

Committing fields to database
-----------------------------

.. _migrations:

Modeltranslation supports the migration system introduced by Django 1.7. Besides the normal workflow as described in Django's
`Migration Docs <https://docs.djangoproject.com/en/1.8/topics/migrations/>`__, you should do a migration whenever one of the following changes have been made to your project:

- Added or removed a language through ``settings.LANGUAGES`` or   ``settings.MODELTRANSLATION LANGUAGES``.
- Registered or unregistered a field through ``WagtailTranslationOptions``.

It doesn't matter if you are starting a fresh project or change an existing one, it's always:

1. ``python manage.py makemigration`` to create a new migration with
   the added or removed fields.

2. ``python manage.py migrate`` to apply the changes.


.. _required_langs:

Required fields
---------------


By default, only the default language of a required field is marked as required (eg. if you have field bar and the default language is pt the only required field will be bar_pt). This behavior can be customized using `required_languages <http://django-modeltranslation.readthedocs.io/en/latest/registration.html#required-fields>`_.

.. _supported_field_matrix:

Supported fields
---------------


The list of all suported fields is available `here <http://django-modeltranslation.readthedocs.io/en/latest/registration.html#supported-fields-matrix>`_.


Supported panels
----------------

The creation of panels for the translation fields supports the following panel classes:

- **FieldPanel**
- **ImageChooserPanel**
- **StreamFieldPanel**
- **MultiFieldPanel**
- **InlinePanel**
