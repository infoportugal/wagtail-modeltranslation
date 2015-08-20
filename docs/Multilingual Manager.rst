********************
Multilingual Manager
********************

Every model registered for translation is patched so that all its managers become subclasses of ``MultilingualManager`` (of course, if a custom manager is defined on the model, its functions is retained). ``MultilingualManager`` simplifies language-aware queries, especially on third-party apps, by rewriting query field names.

Every model manager is patched, not only ``objects`` but also managers inherited from abstract base classes.

For example::

    # Assuming the current language is "pt",
    # these queries returns the same objects
    Foo1 = Foo.objects.filter(introduction__contains='Welcome')
    Foo2 = Foo.objects.filter(introduction_pt__contains='Welcome')

    assert Foo1 == Foo2


It works this way: the translation field name is used, it is changed into the current language field name, based on the current language. Any language-suffixed fields are left untouched, so ``title_es`` wouldn't change, no matter what the current language is.

Rewriting of field names works with operators (like ``__in``, ``__ge``) as well as with
relationship spanning. Moreover, it is also handled on ``Q`` and ``F`` expressions.

These manager methods perform rewriting:

- ``filter()``, ``exclude()``, ``get()``
- ``order_by()``
- ``update()``
- ``only()``, ``defer()``
- ``values()``, ``values_list()``, with :ref:`fallback <fallback>` mechanism
- ``dates()``
- ``select_related()``
- ``create()``, with optional auto-population_ feature

In order not to introduce differences between ``X.objects.create(...)`` and ``X(...)``, model
constructor is also patched and performs rewriting of field names prior to regular initialization.

If one wants to turn rewriting of field names off, this can be easily achieved with
``rewrite(mode)`` method. ``mode`` is a boolean specifying whether rewriting should be applied.
It can be changed several times inside a query. So ``X.objects.rewrite(False)`` turns rewriting off.

``MultilingualManager`` offers one additional method: ``raw_values``. It returns actual values from
the database, without field names rewriting. Useful for checking translated field database value.

Auto-population
---------------

There is special manager method ``populate mode `` which can trigger ``create()`` or
``get_or_create()`` to populate all translation language fields with values from translated original ones. It can be very convenient when working with many languages. So::

    x = Foo.objects.populate(True).create(title='bar')

is equivalent of::

    x = Foo.objects.create(title_pt='bar', title_es='bar', title_fr='bar') ## title_?? for every language


Moreover, some fields can be explicitly assigned different values::

    x = Foo.objects.populate(True).create(title='-- no translation yet --', title_es='hay traducción todavía')

It will result in ``title_es == 'hay traducción todavía'`` and other ``title_?? == '-- no translation yet --'``.

There is another way of altering the current population status, an ``auto_populate`` context
manager::

    from modeltranslation.utils import auto_populate

    with auto_populate(True):
        x = Foo.objects.create(title='bar')

Auto-population takes place also in model constructor, what is extremely useful when loading
non-translated fixtures. Just remember to use the context manager::

     with auto_populate():  # True can be ommited
        call_command('loaddata', 'fixture.json')  # Some fixture loading

        z = Foo(title='bar')
        print z.title_pt, z.title_es, z.title_fr  # prints 'bar bar bar'

There is a more convenient way than calling ``populate`` manager method or entering
``auto_populate`` manager context all the time: :ref:`settings-modeltranslation_auto_populate`
setting. It controls the default population behaviour.


Auto-population modes
---------------------

There are four different population modes:

``False``
    [set by default]

    Auto-population turned off

``True`` or ``'all'``
    [default argument to population altering methods]

    Auto-population turned on, copying translated field value to all other languages
    (unless a translation field value is provided)

``'default'``
    Auto-population turned on, copying translated field value to default language field
    (unless its value is provided)

``'required'``
    Acts like ``'default'``, but copy value only if the original field is non-nullable


.. _fallback:

Falling back
------------

Modeltranslation provides a mechanism to control behaviour of data access in case of empty
translation values. This mechanism affects field access, as well as ``values()`` and ``values_list()`` manager methods.

Here is an example: a writer of some news hasn't specified a French title and content, but only the Spanish and Portuguese ones. Then if a French visitor is viewing the site, we would rather show
him English title/content of the news than having empty strings displayed. This is called *fallback*. ::

    news.title_en = 'English title'
    news.title_fr = ''
    print news.title
    # If current active language is French, it should display the title_de field value ('').
    # But if fallback is enabled, it would display 'English title' instead.

    # Similarly for manager
    news.save()
    print News.objects.filter(pk=news.pk).values_list('title', flat=True)[0]
    # As above: if current active language is French and fallback to English is enabled,
    # it would display 'English title'.

There are several ways of controlling fallback, described below.

.. _fallback_lang:

Fallback languages
------------------

:ref:`modeltranslation_fallback_languages` setting allows to set the order of *fallback
languages*. By default that's the ``DEFAULT_LANGUAGE``.

For example, setting ::

    MODELTRANSLATION_FALLBACK_LANGUAGES = ('en', 'es')

means: if current active language field value is unset, try English value. If it is also unset,
try Portuguese, and so on - until some language yields a non-empty value of the field.

There is also an option to define a fallback by language, using dict syntax::

    MODELTRANSLATION_FALLBACK_LANGUAGES = {
        'default': ('pt', 'es', 'en'),
        'fr': ('es',),
        'uk': ('fr',)
    }

The ``default`` key is required and its value denote languages which are always tried at the end.
With such a setting:

- for `uk` the order of fallback languages is: ``('ru', 'en', 'de', 'fr')``
- for `fr` the order of fallback languages is: ``('de', 'en')`` - Note, that `fr` obviously is not
  a fallback, since its active language and `de` would be tried before `en`
- for `en` and `de` the fallback order is ``('de', 'fr')`` and ``('en', 'fr')``, respectively
- for any other language the order of fallback languages is just ``('en', 'de', 'fr')``

What is more, fallback languages order can be overridden per model, using ``TranslationOptions``::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('title', 'text',)
        fallback_languages = {'default': ('fa', 'km')}  # use Persian and Khmer as fallback for News

Dict syntax is only allowed there.

Even more, all fallbacks may be switched on or off for just some exceptional block of code using::

    from modeltranslation.utils import fallbacks

    with fallbacks(False):
        # Work with values for the active language only

.. _fallback_val:

Fallback values
---------------

But what if current language and all fallback languages yield no field value? Then modeltranslation
will use the field's *fallback value*, if one was defined.

Fallback values are defined in ``TranslationOptions``, for example::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('title', 'text',)
        fallback_values = _('-- sorry, no translation provided --')

In this case, if title is missing in active language and any of fallback languages, news title
will be ``'-- sorry, no translation provided --'`` (maybe translated, since gettext is used).
Empty text will be handled in same way.

Fallback values can be also customized per model field::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('title', 'text',)
        fallback_values = {
            'title': _('-- sorry, this news was not translated --'),
            'text': _('-- please contact our translator (translator@example.com) --')
        }

If current language and all fallback languages yield no field value, and no fallback values are
defined, then modeltranslation will use the field's default value.

.. _fallback_undef:

Fallback undefined
------------------

Another question is what do we consider "no value", on what value should we fall back to other
translations? For text fields the empty string can usually be considered as the undefined value,
but other fields may have different concepts of empty or missing values.

Modeltranslation defaults to using the field's default value as the undefined value (the empty
string for non-nullable ``CharFields``). This requires calling ``get_default`` for every field
access, which in some cases may be expensive.

If you'd like to fall back on a different value or your default is expensive to calculate, provide
a custom undefined value (for a field or model)::

    class NewsTranslationOptions(TranslationOptions):
        fields = ('title', 'text',)
        fallback_undefined = {
            'title': 'no title',
            'text': None
        }

The State of the original field
-------------------------------

As defined by the :ref:`rules`, accessing the original field is guaranteed to
work on the associated translation field of the current language. This applies
to both, read and write operations.

The actual field value (which *can* still be accessed through instance.__dict__['original_field_name']``) however has to
be considered **undetermined** once the field has been registered for translation. Attempts to keep the value in sync with
either the default or current language's field value has raised a boatload of unpredictable side effects in older versions
of modeltranslation.

.. warning::
    Do not rely on the underlying value of the *original field* in any way!

.. todo::
    Perhaps outline effects this might have on the ``update_translation_field``
    management command.