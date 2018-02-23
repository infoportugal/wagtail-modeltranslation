.. _management_commands:

Management Commands
===================

.. _management_commands-wagtail_modeltranslation:

wagtail_modeltranslation
------------------------

wagtail_modeltranslation module adds the following management commands.

.. _management_commands-update_translation_fields:

The ``update_translation_fields`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is a proxy to ``django-modeltranslation``'s own ``update_translation_fields``, for more details read the 
corresponding documentation on `django-modeltranslation docs
<http://django-modeltranslation.readthedocs.io/en/latest/commands.html#the-update-translation-fields-command>`_.

In case modeltranslation was installed in an existing project and you
have specified to translate fields of models which are already synced to the
database, you have to update your database schema.

Unfortunately the newly added translation fields on the model will be empty
then, and your templates will show the translated value of the fields which 
will be empty in this case. To correctly initialize the default translation 
field you can use the ``update_translation_fields`` command:

.. code-block:: console

    $ python manage.py update_translation_fields

.. _management_commands-sync_page_translation_fields:

The ``sync_page_translation_fields`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.8

This command compares the database and translated Page model definition (finding new translation
fields) and provides SQL statements to alter ``wagtailcore_page`` table. You should run this command 
after installation and after adding a new language to your ``settings.LANGUAGES``.

.. code-block:: console

    $ python manage.py sync_page_translation_fields

.. _management_commands-makemigrations_translation:

The ``makemigrations_translation`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.8

``wagtail-modeltranslation`` patches Wagtail's ``Page`` model and as consequence Django's original 
``makemigrations`` commmand will create migrations for ``Page`` which may create conflicts with 
other migrations. To circumvent this issue ``makemigrations_translation`` hides any ``Page`` model changes 
and creates all other migrations as usual. Use this command as an alternative to Django's own 
``makemigrations`` or consider using :ref:`management_commands-makemigrations`.

.. code-block:: console

    $ python manage.py makemigrations_translation

.. _management_commands-migrate_translation:

The ``migrate_translation`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.8

Since :ref:`management_commands-makemigrations_translation` hides any ``Page`` model changes, Django's own
``migrate`` command won't be able to update ``wagtailcore_page`` table with new translation fields. In order to
correctly update the database schema a combination of ``migrate`` followed by :ref:`sync_page_translation_fields` 
is usually required. ``migrate_translation`` provides a shortcut to running these two commands. Use this 
as an alternative to Django's own ``migrate`` or consider using :ref:`management_commands-migrate`.

.. code-block:: console

    $ python manage.py migrate_translation

.. _management_commands-set_translation_url_paths:

The ``set_translation_url_paths`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updates url_path translation fields for all pages.

.. code-block:: console

    $ python manage.py set_translation_url_paths
    

.. _management_commands-wagtail_modeltranslation.makemigrations:

wagtail_modeltranslation.makemigrations
---------------------------------------

To use ``wagtail_modeltranslation.makemigrations`` module commands add ``'wagtail_modeltranslation.makemigrations,'`` 
to ``INSTALLED_APPS``. This module adds the following management commands.

.. _management_commands-makemigrations:

The ``makemigrations`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is a proxy for :ref:`management_commands-makemigrations_translation`. It has the added benefit of 
overriding Django's own ``makemigrations`` allowing you to run ``makemigrations`` safely without creating 
spurious ``Page`` migrations.

.. code-block:: console

    $ python manage.py makemigrations

.. _management_commands-makemigrations_original:

The ``makemigrations_original`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Django's ``makemigrations`` is overriden by ``wagtail-modeltranslation``'s version use 
``makemigrations_original`` to run the Django's original ``makemigrations`` command. Please note 
this will likely create invalid ``Page`` migrations, do this only if you know what you're doing.

.. code-block:: console

    $ python manage.py makemigrations_original


.. _management_commands-wagtail_modeltranslation.migrate:

wagtail_modeltranslation.migrate
---------------------------------

To use ``wagtail_modeltranslation.migrate`` module commands add ``'wagtail_modeltranslation.migrate,'`` 
to ``INSTALLED_APPS``. This module adds the following management commands.

.. _management_commands-migrate:

The ``migrate`` Command
~~~~~~~~~~~~~~~~~~~~~~~

This command is a proxy for :ref:`management_commands-migrate_translation`. It has the added benefit of 
overriding Django's own ``migrate`` saving the need to additionally run :ref:`sync_page_translation_fields`. 
See `issue #175
<https://github.com/infoportugal/wagtail-modeltranslation/issues/175#issuecomment-368046055>`_ to understand 
how this command can be used to create translation fields in a test database.

.. code-block:: console

    $ python manage.py migrate

.. _management_commands-migrate_original:

The ``migrate_original`` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Django's ``migrate`` is overriden by ``wagtail-modeltranslation``'s version use 
``migrate_original`` to run the Django's original ``migrate`` command. Please note 
this will not update ``wagtailcore_page`` table with new translation fields, use 
:ref:`sync_page_translation_fields` for that.

.. code-block:: console

    $ python manage.py migrate_original
