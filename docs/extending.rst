.. _extending:

Extending
=========

JS "ready" event
----------------

``wagtail-modeltranslation`` runs custom JS in order for it to offer the full experience,
and will generate an event called ``wagtail-modeltranslation:buildSets:done`` on the
``document`` that can be listened for before your own JS runs

.. code-block:: javascript

    document.addEventListener(`wagtail-modeltranslation:buildSets:done`, evt => {
        // Any code here will run only once wagtail-modeltranslation has
        // finished updating the DOM with the content it needs, and class
        // assignments necessary for toggling locale field visibilities.
    });
