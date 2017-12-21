# coding: utf-8
import imp

import django
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.utils.translation import get_language, trans_real
from modeltranslation import settings as mt_settings, translator

from wagtail_modeltranslation.tests.test_settings import TEST_SETTINGS

models = translation = None


class dummy_context_mgr():
    def __enter__(self):
        return None

    def __exit__(self, _type, value, traceback):
        return False


@override_settings(**TEST_SETTINGS)
class WagtailModeltranslationTransactionTestBase(TransactionTestCase):
    cache = django_apps
    synced = False

    @classmethod
    def setUpClass(cls):
        """
        Prepare database:
        * Call syncdb to create tables for tests.models (since during
        default testrunner's db creation wagtail_modeltranslation.tests was not in INSTALLED_APPS
        """
        super(WagtailModeltranslationTransactionTestBase, cls).setUpClass()
        if not WagtailModeltranslationTransactionTestBase.synced:
            # In order to perform only one syncdb
            WagtailModeltranslationTransactionTestBase.synced = True
            mgr = (override_settings(**TEST_SETTINGS) if django.VERSION < (1, 8)
                   else dummy_context_mgr())
            with mgr:
                # 1. Reload translation in case USE_I18N was False
                from django.utils import translation as dj_trans
                imp.reload(dj_trans)

                # 2. Reload MT because LANGUAGES likely changed.
                imp.reload(mt_settings)
                imp.reload(translator)

                # reload the translation module to register the Page model
                # and also edit_handlers so any patches made to Page are reapplied
                from wagtail_modeltranslation import translation as wag_translation, translator as wag_translator
                from wagtail.wagtailadmin import edit_handlers
                import sys
                del cls.cache.all_models['wagtailcore']
                sys.modules.pop('wagtail_modeltranslation.translation.pagetr', None)
                sys.modules.pop('wagtail.wagtailcore.models', None)
                imp.reload(wag_translation)
                imp.reload(wag_translator)
                imp.reload(edit_handlers)  # so Page can be repatched by edit_handlers
                wagtailcore_args = []
                if django.VERSION < (1, 11):
                    wagtailcore_args = [cls.cache.all_models['wagtailcore']]
                cls.cache.get_app_config('wagtailcore').import_models(*wagtailcore_args)

                # Reload the patching class to update the imported translator
                # in order to include the newly registered models
                from wagtail_modeltranslation import patch_wagtailadmin
                imp.reload(patch_wagtailadmin)

                # 3. Reset test models (because autodiscover have already run, those models
                #    have translation fields, but for languages previously defined. We want
                #    to be sure that 'de' and 'en' are available)
                del cls.cache.all_models['tests']
                sys.modules.pop('wagtail_modeltranslation.tests.models', None)
                sys.modules.pop('wagtail_modeltranslation.tests.translation', None)
                tests_args = []
                if django.VERSION < (1, 11):
                    tests_args = [cls.cache.all_models['tests']]
                cls.cache.get_app_config('tests').import_models(*tests_args)

                # 4. Autodiscover
                from modeltranslation.models import handle_translation_registrations
                handle_translation_registrations()

                # 5. makemigrations
                from django.db import connections, DEFAULT_DB_ALIAS
                call_command('makemigrations_translation', verbosity=2, interactive=False,
                             database=connections[DEFAULT_DB_ALIAS].alias)

                # 6. Syncdb
                call_command('migrate', verbosity=0, migrate=False, interactive=False, run_syncdb=True,
                             database=connections[DEFAULT_DB_ALIAS].alias, load_initial_data=False)

                # 7. Make sure Page translation fields are created
                call_command('sync_page_translation_fields', interactive=False, verbosity=0, database=connections[DEFAULT_DB_ALIAS].alias)

                # 8. patch wagtail models
                from wagtail_modeltranslation.patch_wagtailadmin import patch_wagtail_models
                patch_wagtail_models()

                # A rather dirty trick to import models into module namespace, but not before
                # tests app has been added into INSTALLED_APPS and loaded
                # (that's why this is not imported in normal import section)
                global models, translation
                from wagtail_modeltranslation.tests import models, translation # NOQA

    def setUp(self):
        self._old_language = get_language()
        trans_real.activate('de')

    def tearDown(self):
        trans_real.activate(self._old_language)


class WagtailModeltranslationTestBase(TestCase, WagtailModeltranslationTransactionTestBase):
    pass


class WagtailModeltranslationTest(WagtailModeltranslationTestBase):
    """
    Test of the modeltranslation features with Wagtail models (Page and Snippet)
    """

    @classmethod
    def setUpClass(cls):
        super(WagtailModeltranslationTest, cls).setUpClass()

        # Delete the default wagtail pages from db
        from wagtail.wagtailcore.models import Page
        Page.objects.delete()

    def test_page_fields(self):
        fields = dir(models.PatchTestPage())

        # Check if Page fields are being created
        self.assertIn('title_en', fields)
        self.assertIn('title_de', fields)
        self.assertIn('slug_en', fields)
        self.assertIn('slug_de', fields)
        self.assertIn('seo_title_en', fields)
        self.assertIn('seo_title_de', fields)
        self.assertIn('search_description_en', fields)
        self.assertIn('search_description_de', fields)
        self.assertIn('url_path_en', fields)
        self.assertIn('url_path_de', fields)

        # Check if subclass fields are being created
        self.assertIn('description_en', fields)
        self.assertIn('description_de', fields)

    def test_snippet_fields(self):
        fields = dir(models.PatchTestSnippet())

        self.assertIn('name', fields)
        self.assertIn('name_en', fields)
        self.assertIn('name_de', fields)

    def check_fieldpanel_patching(self, panels, name='name'):
        # Check if there is one panel per language
        self.assertEquals(len(panels), 2)

        # Validate if the created panels are instances of FieldPanel
        from wagtail.wagtailadmin.edit_handlers import FieldPanel
        self.assertIsInstance(panels[0], FieldPanel)
        self.assertIsInstance(panels[1], FieldPanel)

        # Check if both field names were correctly created
        fields = [panel.field_name for panel in panels]
        self.assertListEqual([name + '_de', name + '_en'], fields)

    def check_imagechooserpanel_patching(self, panels, name='image'):
        # Check if there is one panel per language
        self.assertEquals(len(panels), 2)

        from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
        self.assertIsInstance(panels[0], ImageChooserPanel)
        self.assertIsInstance(panels[1], ImageChooserPanel)

        # Check if both field names were correctly created
        fields = [panel.field_name for panel in panels]
        self.assertListEqual([name + '_de', name + '_en'], fields)

    def check_fieldrowpanel_patching(self, panels, child_name='other_name'):
        # Check if the fieldrowpanel still exists
        self.assertEqual(len(panels), 1)

        from wagtail.wagtailadmin.edit_handlers import FieldRowPanel
        self.assertIsInstance(panels[0], FieldRowPanel)

        # Check if the children were correctly patched using the fieldpanel test
        children_panels = panels[0].children

        self.check_fieldpanel_patching(panels=children_panels, name=child_name)

    def check_streamfieldpanel_patching(self, panels):
        # Check if there is one panel per language
        self.assertEquals(len(panels), 2)

        from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
        self.assertIsInstance(panels[0], StreamFieldPanel)
        self.assertIsInstance(panels[1], StreamFieldPanel)

        # Check if both field names were correctly created
        fields = [panel.field_name for panel in panels]
        self.assertListEqual(['body_de', 'body_en'], fields)

        # Fetch one of the streamfield panels to see if the block was correctly created
        child_block = list(models.StreamFieldPanelPage.body_en.field.stream_block.child_blocks.items())

        self.assertEquals(len(child_block), 1)

        from wagtail.wagtailcore.blocks import CharBlock
        self.assertEquals(child_block[0][0], 'text')
        self.assertIsInstance(child_block[0][1], CharBlock)

    def check_multipanel_patching(self, panels):
        # There are three multifield panels, one for each of the available
        # children panels
        self.assertEquals(len(panels), 3)

        from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel
        self.assertIsInstance(panels[0], MultiFieldPanel)
        self.assertIsInstance(panels[1], MultiFieldPanel)
        self.assertIsInstance(panels[2], MultiFieldPanel)

        fieldpanel = panels[0].children
        imagechooser = panels[1].children
        fieldrow = panels[2].children

        self.check_fieldpanel_patching(panels=fieldpanel)
        self.check_imagechooserpanel_patching(panels=imagechooser)
        self.check_fieldrowpanel_patching(panels=fieldrow)

    def check_inlinepanel_patching(self, panels):
        # The inline panel has all the available combination of children panels making
        # a grand total of 8 panels
        self.assertEqual(len(panels), 8)

        # The first 2 panels are fieldpanels, the following 2 are imagechooserpanels,
        # next is a fieldrowpanel and finally there are 3 multifieldpanels
        self.check_fieldpanel_patching(panels=panels[0:2], name='field_name')
        self.check_imagechooserpanel_patching(panels=panels[2:4], name='image_chooser')
        self.check_fieldrowpanel_patching(panels=panels[4:5], child_name='fieldrow_name')
        self.check_multipanel_patching(panels=panels[5:8])

    def test_page_patching(self):
        self.check_fieldpanel_patching(panels=models.FieldPanelPage.content_panels)
        self.check_imagechooserpanel_patching(panels=models.ImageChooserPanelPage.content_panels)
        self.check_fieldrowpanel_patching(panels=models.FieldRowPanelPage.content_panels)
        self.check_streamfieldpanel_patching(panels=models.StreamFieldPanelPage.content_panels)
        self.check_multipanel_patching(panels=models.MultiFieldPanelPage.content_panels)

        # In spite of the model being the InlinePanelPage the panels are patch on the related model
        # which is the PageInlineModel
        self.check_inlinepanel_patching(panels=models.PageInlineModel.panels)

    def test_snippet_patching(self):
        self.check_fieldpanel_patching(panels=models.FieldPanelSnippet.panels)
        self.check_imagechooserpanel_patching(panels=models.ImageChooserPanelSnippet.panels)
        self.check_fieldrowpanel_patching(panels=models.FieldRowPanelSnippet.panels)
        self.check_streamfieldpanel_patching(panels=models.StreamFieldPanelSnippet.panels)
        self.check_multipanel_patching(panels=models.MultiFieldPanelSnippet.panels)

        # In spite of the model being the InlinePanelSnippet the panels are patch on the related model
        # which is the SnippetInlineModel
        self.check_inlinepanel_patching(panels=models.SnippetInlineModel.panels)

    def test_page_form(self):
        """
        In this test we use the InlinePanelPage model because it has all the possible "patchable" fields
        so if the created form has all fields the the form was correctly patched
        """

        page_edit_handler = models.InlinePanelPage.get_edit_handler()

        form = page_edit_handler.get_form_class(models.InlinePanelPage)

        page_base_fields = ['slug_de', 'slug_en', 'seo_title_de', 'seo_title_en', 'search_description_de',
                            'search_description_en', u'show_in_menus', u'go_live_at', u'expire_at']

        try:
            # python 3
            self.assertCountEqual(page_base_fields, form.base_fields.keys())
        except AttributeError:
            # python 2.7
            self.assertItemsEqual(page_base_fields, form.base_fields.keys())

        inline_model_fields = ['field_name_de', 'field_name_en', 'image_chooser_de', 'image_chooser_en',
                               'fieldrow_name_de', 'fieldrow_name_en', 'name_de', 'name_en', 'image_de', 'image_en',
                               'other_name_de', 'other_name_en']

        related_formset_form = form.formsets['related_page_model'].form

        try:
            # python 3
            self.assertCountEqual(inline_model_fields, related_formset_form.base_fields.keys())
        except AttributeError:
            # python 2.7
            self.assertItemsEqual(inline_model_fields, related_formset_form.base_fields.keys())

    def test_snippet_form(self):
        """
        In this test we use the InlinePanelSnippet model because it has all the possible "patchable" fields
        so if the created form has all fields the the form was correctly patched
        """
        from wagtail.wagtailsnippets.views.snippets import get_snippet_edit_handler
        snippet_edit_handler = get_snippet_edit_handler(models.InlinePanelSnippet)

        form = snippet_edit_handler.get_form_class(models.InlinePanelSnippet)

        inline_model_fields = ['field_name_de', 'field_name_en', 'image_chooser_de', 'image_chooser_en',
                               'fieldrow_name_de', 'fieldrow_name_en', 'name_de', 'name_en', 'image_de', 'image_en',
                               'other_name_de', 'other_name_en']

        related_formset_form = form.formsets['related_snippet_model'].form

        try:
            # python 3
            self.assertCountEqual(inline_model_fields, related_formset_form.base_fields.keys())
        except AttributeError:
            # python 2.7
            self.assertItemsEqual(inline_model_fields, related_formset_form.base_fields.keys())

    def test_duplicate_slug(self):
        from wagtail.wagtailcore.models import Site
        # Create a test Site with a root page
        root = models.TestRootPage(title='title', depth=1, path='0001', slug_en='slug_en', slug_de='slug_de')
        root.save()

        site = Site(root_page=root)
        site.save()

        # Add children to the root
        child = root.add_child(
            instance=models.TestSlugPage1(title='child1', slug_de='child', slug_en='child-en', depth=2, path='00010001')
        )

        child2 = root.add_child(
            instance=models.TestSlugPage2(title='child2', slug_de='child-2', slug_en='child2-en', depth=2,
                                          path='00010002')
        )

        # Clean should work fine as the two slugs are different
        child2.clean()

        # Make the slug equal to test if the duplicate is detected
        child2.slug_de = 'child'

        self.assertRaises(ValidationError, child2.clean)

    def test_original_slug_update(self):
        from wagtail.wagtailcore.models import Page
        # save the page in the default language
        root = models.TestRootPage(title='original slug', title_de='originalschnecke', depth=1, path='0002',
                                   slug_en='test-slug-en', slug_de='test-slug-de')
        root.save()

        # some control checks, we don't expect any surprises here
        self.assertEqual(root.slug, 'test-slug-de', 'slug has the wrong value.')
        self.assertEqual(root.slug_de, 'test-slug-de', 'slug_de has the wrong value.')
        self.assertEqual(root.slug_en, 'test-slug-en', 'slug_en has the wrong value.')

        # fetches the correct Page using slug
        page = Page.objects.filter(slug='test-slug-de').first()
        self.assertEqual(page.specific, root, 'The wrong page was retrieved from DB.')

        trans_real.activate('en')

        # fetches the correct Page using slug using non-default language
        page = Page.objects.rewrite(False).filter(slug='test-slug-de').first()
        self.assertEqual(page.specific, root, 'The wrong page was retrieved from DB.')

        # save the page 2 in the non-default language
        root2 = models.TestRootPage(title='original slug 2', title_de='originalschnecke 2', depth=1, path='0003',
                                    slug_en='test-slug2-en', slug_de='test-slug2-de')
        root2.save()

        # sanity checks
        self.assertEqual(root2.slug, 'test-slug2-en', 'slug has the wrong value.')
        self.assertEqual(root2.slug_de, 'test-slug2-de', 'slug_de has the wrong value.')
        self.assertEqual(root2.slug_en, 'test-slug2-en', 'slug_en has the wrong value.')

        # fetches the correct Page using slug using non-default language
        page = Page.objects.rewrite(False).filter(slug='test-slug2-de').first()
        self.assertEqual(page.specific, root2, 'The wrong page was retrieved from DB.')

        trans_real.activate('de')

        # fetches the correct Page using slug using default language
        page = Page.objects.rewrite(False).filter(slug='test-slug2-de').first()
        self.assertEqual(page.specific, root2, 'The wrong page was retrieved from DB.')



    def test_relative_url(self):
        from wagtail.wagtailcore.models import Site
        # Create a test Site with a root page
        root = models.TestRootPage(title='title slugurl', depth=1, path='0004',
                                   slug_en='title_slugurl_en', slug_de='title_slugurl_de')
        root.save()
        site = Site(root_page=root)
        site.save()

        # Add children to the root
        child = root.add_child(
            instance=models.TestSlugPage1(title='child1 slugurl',
                                          slug_en='child-slugurl-en', slug_de='child-slugurl-de',
                                          depth=2, path='00040001')
        )
        child.save_revision().publish()

        url_1_de = child.relative_url(site)
        self.assertEqual(url_1_de, '/de/child-slugurl-de/',
                         'When using the default language, slugurl produces the wrong url.')

        trans_real.activate('en')

        url_1_en = child.relative_url(site)
        self.assertEqual(url_1_en, '/en/child-slugurl-en/',
                         'When using non-default language, slugurl produces the wrong url.')

        # Add children using non-default language
        child2 = root.add_child(
            instance=models.TestSlugPage2(title='child2 slugurl', title_de='child2 slugurl DE',
                                          slug_de='child2-slugurl-de', slug_en='child2-slugurl-en',
                                          depth=2, path='00040002')
        )
        child2.save_revision().publish()

        url_2_en = child2.relative_url(site)
        self.assertEqual(url_2_en, '/en/child2-slugurl-en/',
                         'When using non-default language, slugurl produces the wrong url.')

        trans_real.activate('de')

        url_2_de = child2.relative_url(site)
        self.assertEqual(url_2_de, '/de/child2-slugurl-de/',
                         'When using non-default language, slugurl produces the wrong url.')

    def test_searchfield_patching(self):
        # Check if the search fields have the original field plus the translated ones
        expected_fields = ['title', 'title_de', 'title_en', 'description', 'description_de', 'description_en']

        model_search_fields = [searchfield.field_name for searchfield in models.PatchTestPage.search_fields]

        try:
            # python 3
            self.assertCountEqual(expected_fields, model_search_fields)
        except AttributeError:
            # python 2.7
            self.assertItemsEqual(expected_fields, model_search_fields)

    def test_streamfield_fallback(self):
        body_text = '[{"value": "Some text", "type": "text"}]'
        page = models.StreamFieldPanelPage(title='Streamfield Fallback', slug='streamfield_fallback',
                                           depth=1, path='0005', body=body_text)
        page.save()

        self.assertEqual(str(page.body), '<div class="block-text">Some text</div>')

        trans_real.activate('en')

        self.assertEqual(str(page.body), '<div class="block-text">Some text</div>',
                         'page.body did not fallback to original language.')

    def test_set_url_path(self):
        from wagtail.wagtailcore.models import Site
        # Create a test Site with a root page
        root = models.TestRootPage(title='url paths', depth=1, path='0006', slug='url-path-slug')
        root.save()

        site = Site(root_page=root)
        site.save()

        # Add children to the root
        child = root.add_child(
            instance=models.TestSlugPage1(title='child', slug='child', depth=2, path='00060001')
        )
        child.save()

        # Add grandchildren to the root
        grandchild = child.add_child(
            instance=models.TestSlugPage1(title='grandchild', slug='grandchild', depth=2, path='000600010001')
        )
        grandchild.save()

        self.assertEqual(child.url_path_de, '/child/')
        self.assertEqual(child.url_path_en, '/child/')
        self.assertEqual(grandchild.url_path_de, '/child/grandchild/')
        self.assertEqual(grandchild.url_path_en, '/child/grandchild/')

        grandchild.slug_de = 'grandchild1'
        grandchild.save()

        self.assertEqual(grandchild.url_path_de, '/child/grandchild1/')
        self.assertEqual(grandchild.url_path_en, '/child/grandchild1/')

        grandchild.slug_en = 'grandchild1_en'
        grandchild.save()

        self.assertEqual(grandchild.url_path_de, '/child/grandchild1/')
        self.assertEqual(grandchild.url_path_en, '/child/grandchild1_en/')

        # Children url paths should update when parent changes
        child.slug_en = 'child_en'
        child.save()

        self.assertEqual(child.url_path_de, '/child/')
        self.assertEqual(child.url_path_en, '/child_en/')

        # We should retrieve grandchild with the below command:
        grandchild_new = models.TestSlugPage1.objects.get(id=grandchild.id)
        self.assertEqual(grandchild_new.url_path_en, '/child_en/grandchild1_en/')
        self.assertEqual(grandchild_new.url_path_de, '/child/grandchild1/')
