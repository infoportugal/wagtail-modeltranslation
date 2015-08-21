-----------------------------------
Change Log
-----------------------------------

v0.2.2:
- Added duplicate content buttons to translated StreamFieldPanels;

v0.2.1:
- Fixed missing templatetags folder on pypi package;

v0.2:
- Support for StreamFields;
- No more django-modeltranslation dependency;

v0.1.5

- Fixed required fields related bug

v0.1.4

- Support for wagtailsearch and wagtailsnippets

v0.1.3

- Support for translated inline panels #8: https://github.com/infoportugal/wagtail-modeltranslation/issues/8

v0.1.2

- Fixed Problem updating field with null value #6: https://github.com/infoportugal/wagtail-modeltranslation/issues/6

v0.1.1

- Fixed url_path issue caused by a browser with language different from settings.LANGUAGE_CODE

v0.1

- Minor release working but lacks full test coverage.
- Last version had required fields validation problems, now fixed.

v0.0.9

- Fixed issue that causes duplicated translation fields, preventing auto-slug from working properly.

v0.0.8

- Fixed issue related to deleting a non existing key on PAGE_EDIT_HANDLER dict

v0.0.7

- Fixed set_url_path() translatable model method

v0.0.6

- Fixed js issue related to auto-generating slugs

v0.0.5

- Now using django-modeltranslation 0.9.1;
- Fixed problem related to slug field fallbacks;

v0.0.4

** IMPORTANT: ** make sure that TranslationMixin comes before Page class on model inheritance

- Fix enhancement #1: url_path translation field
- Now includes a template tag that returns current page url to corresponding translated url
- New management command to update url_path translation fields - **set\_translation\_url\_paths**

v0.0.3

- New methods;
- Now supports required fields;
- Fixed issue related to browser locale;

v0.0.2

- Prepopulated fields now works for translated fields (title and slug)