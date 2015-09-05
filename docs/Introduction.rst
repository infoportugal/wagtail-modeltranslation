*************
Introduction
*************

Creating multilingual sites
===========================

**I18n**

Django and Wagtail CMS have implemented Internationalisation (I18n) in their frameworks. Hooks are provided for translating
strings such as literals.  Furthermore, **locale language files** are included. This is where the translated text of the
frameworks is stored.

When writing your own apps, it is recommended that you use Il18n. If you need guidance, you can read the  `Django Internalization
Documentation <https://docs.djangoproject.com/en/1.8/topics/i18n/translation/>`_.

**Wagtail-modeltranslation**

Another important component in the translation equation is the content stored in database fields. This is where
wagtail-modeltranslation comes into play.

Wagtail-modeltranslation is a fork of django-modeltranslation designed to define the fields that need to be translated.
In Wagtail, translation fields are displayed and edited together on the same page in the Wagtail admin interface. Translated
fields can be used in your templates and as you would use any other field.


Some of the advantages of wagtail-modeltranslation
--------------------------------------------------

* The same template is used for multiple languages
* The document tree is simpler with no need to have a separate branch for each language
* Languages can be added without changing existing models or views
* Translation fields are stored in the same table (no expensive joins)
* Can handle more than just text fields
* Wagtail admin integration
* Flexible fallbacks, auto-population and more!
* Default Page model has translatable fields by default
* StreamFields are supported
* Easy to implement


Examples used in this document
------------------------------
We will be using a fictitious model ``foo`` in the coding examples.


Wagtail-modeltranslation and Modeltranslation
---------------------------------------------
This document is for the most part an adaptation of the django-modeltranslation documentation, so we will refer to
``wagtail-modeltranslation`` when the material discussed is specific to Wagtail CMS and ``modeltranslation`` when it
is applicable to both wagtail-modeltranslation and django-modeltranslaton. You don't need to distinguish between the
two since wagtail-modeltranslation includes all the functionalities of django-modeltranslation.