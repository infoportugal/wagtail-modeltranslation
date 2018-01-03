.. _template tags:

=============
Template Tags
=============

change_lang
===========

Use this template tag to get the url of the current page in another language. The only parameter of this template tag is the language code the we want to get the url. Below is an example where we want to get the url of the current page in portuguese.

.. code-block:: django

    {% change_lang 'pt' %}


get_available_languages_wmt
===========================

Use this template tag to get the current languages from MODELTRANSLATION_LANGUAGES (or LANGUAGES) from your setting file (or the default settings).

.. code-block:: django

    {% get_available_languages_wmt as languages %}
    {% for language in languages %}
    ...
    {% endfor %}
