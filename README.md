# Wagtail modeltranslation

Simple app containing a mixin model that integrates modeltranslation
(https://github.com/deschler/django-modeltranslation) into wagtail panels system.

![alt tag](https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true)

## Quick start

1. Make sure you have django-modeltranslation installed:

        pip install django-modeltranslation

2. Add "wagtail_modeltranslation" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = (
            ...
            'wagtail_modeltranslation',
            'modeltranslation',
            ...
        )

3. Use TranslationMixin in order to integrate django-modeltranslation with Wagtail admin. ** IMPORTANT: ** make sure that TranslationMixin is declared before Page class on model inheritance. Like following:

        from wagtail_modeltranslation.models import TranslationMixin
        class FooModel(TranslationMixin, Page):
            foo = models.CharField()
        FooModel.panels = [...]

4. Visit django-modeltranslation for documentation on how to implement translation fields: http://django-modeltranslation.readthedocs.org/en/latest/

5. In order to update pages url_path field use **"set\_translation\_url\_paths"** instead of original "set\_url\_paths"

6. Use **"change_lang"** template tag to fetch translated urls based on translated slugs:

        {% load modeltranslation %}
        <li class="dropdown">
            <a data-toggle="dropdown" class="dropdown-toggle" data-hover="dropdown" href="#">{{ LANGUAGE_CODE }}<i class="fa fa-angle-down ml5"></i></a>
            <ul class="dropdown-menu" id="language-dropdown">
                {% for lang in languages %}
                {% if lang.0 != LANGUAGE_CODE %}
                <li tabindex="-1"><a href="{% change_lang lang.0 %}">{{ lang.1 }}</a></li>
                {% endif %}
                {% endfor %}
            </ul>
        </li>

## Release Notes

## v0.0.8

- Fixed issue related to deleting a non existing key on PAGE_EDIT_HANDLER dict

## v0.0.7

- Fixed set_url_path() translatable model method

### v0.0.6

- Fixed js issue related to auto-generating slugs

### v0.0.5

- Now using django-modeltranslation 0.9.1;
- Fixed problem related to slug field fallbacks;

### v0.0.4

** IMPORTANT: ** make sure that TranslationMixin comes before Page class on model inheritance

- Fix enhancement #1: url_path translation field
- Now includes a template tag that returns current page url to corresponding translated url
- New management command to update url_path translation fields - **set\_translation\_url\_paths**

### v0.0.3

- New methods;
- Now supports required fields;
- Fixed issue related to browser locale;

### v0.0.2

- Prepopulated fields now works for translated fields (title and slug)
