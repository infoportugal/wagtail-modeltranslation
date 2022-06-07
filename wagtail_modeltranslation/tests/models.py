from django.db import models
from django.http import HttpResponse
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from modelcluster.models import ClusterableModel


# Wagtail Models
class TestRootPage(Page):
    parent_page_types = []
    subpage_types = ['tests.TestSlugPage1', 'tests.TestSlugPage2']


class TestSlugPage1(Page):
    pass


class TestSlugPage2(Page):
    pass


class TestSlugPage1Subclass(TestSlugPage1):
    pass


class PatchTestPage(Page):
    description = models.CharField(max_length=50)

    search_fields = (
        index.SearchField('title'),
        index.SearchField('description'),
    )


@register_snippet
class PatchTestSnippetNoPanels(models.Model):
    name = models.CharField(max_length=10)


@register_snippet
class PatchTestSnippet(PatchTestSnippetNoPanels):

    panels = [
        FieldPanel('name')
    ]


# ######### Snippet Patching Models

@register_snippet
class FieldPanelSnippet(models.Model):
    name = models.CharField(max_length=10)

    panels = [
        FieldPanel('name')
    ]


@register_snippet
class ImageChooserPanelSnippet(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
    )

    panels = [
        ImageChooserPanel('image'),
    ]


@register_snippet
class FieldRowPanelSnippet(models.Model):
    other_name = models.CharField(max_length=10)

    panels = [
        FieldRowPanel([
            FieldPanel('other_name'),
        ]),
    ]


@register_snippet
class StreamFieldPanelSnippet(models.Model):
    body = StreamField([
        ('text', blocks.CharBlock(max_length=10))
    ])

    panels = [
        StreamFieldPanel('body')
    ]


class MultiFieldPanelBase(models.Model):
    name = models.CharField(max_length=10)
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    other_name = models.CharField(max_length=10)
    panels = [
        MultiFieldPanel(
            FieldPanelSnippet.panels
        ),
        MultiFieldPanel(
            ImageChooserPanelSnippet.panels
        ),
        MultiFieldPanel(
            FieldRowPanelSnippet.panels
        ),
    ]

    class Meta:
        abstract = True


@register_snippet
class MultiFieldPanelSnippet(MultiFieldPanelBase):
    panels = MultiFieldPanelBase.panels


class BaseInlineModel(MultiFieldPanelBase):
    field_name = models.CharField(max_length=10)

    image_chooser = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )

    fieldrow_name = models.CharField(max_length=10)

    panels = [
        FieldPanel('field_name'),
        ImageChooserPanel('image_chooser'),
        FieldRowPanel([
            FieldPanel('fieldrow_name'),
        ]),
    ] + MultiFieldPanelBase.panels


class SnippetInlineModel(BaseInlineModel):
    page = ParentalKey(
        'tests.InlinePanelSnippet',
        related_name='related_snippet_model',
        on_delete=models.CASCADE,
    )


@register_snippet
class InlinePanelSnippet(ClusterableModel):
    panels = [
        InlinePanel('related_snippet_model')
    ]


# ######### Page Patching Models

class FieldPanelPage(Page):
    name = models.CharField(max_length=50)

    content_panels = [
        FieldPanel('name'),
    ]


class ImageChooserPanelPage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    content_panels = [
        ImageChooserPanel('image'),
    ]


class FieldRowPanelPage(Page):
    other_name = models.CharField(max_length=10)

    content_panels = [
        FieldRowPanel([
            FieldPanel('other_name'),
        ]),
    ]


class StreamFieldPanelPage(Page):
    body = StreamField([
        ('text', blocks.CharBlock(max_length=10))
    ], blank=False)  # since wagtail 1.12 StreamField's blank defaults to False

    content_panels = [
        StreamFieldPanel('body')
    ]


class MultiFieldPanelPage(Page):
    name = models.CharField(max_length=50)
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    other_name = models.CharField(max_length=10)
    content_panels = [
        MultiFieldPanel(
            FieldPanelPage.content_panels
        ),
        MultiFieldPanel(
            ImageChooserPanelPage.content_panels
        ),
        MultiFieldPanel(
            FieldRowPanelPage.content_panels
        ),
    ]


class PageInlineModel(BaseInlineModel):
    page = ParentalKey('tests.InlinePanelPage', related_name='related_page_model')


class InlinePanelPage(Page):
    content_panels = [
        InlinePanel('related_page_model')
    ]


class RoutablePageTest(RoutablePageMixin, Page):
    @route(r'^archive/year/1984/$')
    def archive_for_1984(self, request):
        return HttpResponse("we were always at war with eastasia")

    @route(r'^archive/year/(\d+)/$')
    def archive_by_year(self, request, year):
        return HttpResponse("ARCHIVE BY YEAR: " + str(year))
