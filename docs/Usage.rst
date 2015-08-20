
Accessing translated fields
===========================

Modeltranslation changes the behaviour of the translated fields. To explain this consider the Foo
example from the :ref:`Registering Models` chapter again. The original ``Foo`` model:

.. code-block:: console

    class Foo(TranslationMixin, Page):
        introduction = models.CharField(max_length=255)
        body = RichtextField(blank=True)

Now that it is registered with wagtail-modeltranslation, the model looks like this - note the additional fields automatically added by the app:

.. code-block:: console

   class Foo(TranslationMixin, Page):
      introduction = models.CharField(max_length=255)  # original/translated field
      introduction_pt = models.CharField(null=True, blank=True, max_length=255)  # default translation field
      introduction_es = models.CharField(null=True, blank=True, max_length=255)  # translation field
      introduction_fr = models.CharField(null=True, blank=True, max_length=255)  # translation field
      body = RichTextField(blank=True)  # original/translated field
      body_pt = RichTextField(null=True, blank=True)  # default translation field
      body_es = RichTextField(null=True, blank=True)  # translation field
      body_fr = RichTextField(null=True, blank=True)  # translation field

The example above assumes that the default language is ``pt``, therefore the ``introduction_pt`` and ``body_pt`` fields are marked as the *default translation fields*. If the default language were ``fr``, then ``introduction_fr`` and ``body_fr`` would be the *default translation fields*.

.. warning::

   The ``title`` field is inherited from the Page model; if you try to create a field called ``title`` in one of your ``models`` you will get a warning messaqe. You can include the ``title field`` in ``translation.py`` and in the ``content_panels`` since it is inherited.

.. code-block:: console

    # .models
    HomePage.content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('introduction', classname="full"),
        FieldPanel('body', classname="full"),
        InlinePanel(HomePage, 'carousel_items', label="Carousel items"),
        InlinePanel(HomePage, 'related_links', label="Related links"),
        ]


.. code-block:: console

      # translation.py
      from .models import Foo
      from wagtail_modeltranslation.translator import TranslationOptions
      from wagtail_modeltranslation.decorators import register

      @register(Foo)
      class FooTR(TranslationOptions):
       fields = (
          'title',
          'introduction',
          'body',
       )

.. _rules:

Rules for Translated Field Access
---------------------------------

The following rules apply to setting and getting the value of the original and the translation fields:

**Rule 1**

    Reading the value from the original field returns the value translated to
    the current language.

**Rule 2**

    Assigning a value to the original field updates the value in the associated
    current language translation field.

**Rule 3**

    If both fields - the original and the current language translation field -
    are updated at the same time, the current language translation field wins.

    .. note:: This can only happen in the model's constructor or
        ``objects.create``. There is no other situation which can be considered
        *changing several fields at the same time*.


Examples of translated field access
------------------------------------

Because the whole point of using the wagtail-modeltranslation app is translating dynamic content, the fields marked for
translation are somehow special when it comes to accessing them. The value returned by a translated field is depending on
the current language setting. **Language setting** refers to the Django ``set_language`` view and the corresponding ``get_lang``
function.

Assuming the current language is ``pt`` in the Foo example above, the translated ``introduction`` field will return the value from the ``introduction_pt`` field::

    # Assuming the current language is "pt"
    n = News.objects.all()[0]
    t = n.introduction  # returns the Portuguese translation

    # Assuming the current language is "pt"
    t = n.introduction  # returns the Portuguese translation

This feature is implemented using Python descriptors making it happen without the need to touch the original model classes in any way. The descriptor uses the ``django.utils.i18n.get_language`` function to determine the current language.