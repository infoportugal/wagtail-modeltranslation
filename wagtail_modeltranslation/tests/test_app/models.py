from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail_modeltranslation.models import TranslationMixin, SnippetsTranslationMixin


class News(models.Model):
    class Meta:
        app_label = 'test_app'

    title = models.CharField(max_length=50)
    visits = models.SmallIntegerField(blank=True, null=True)


class Other(models.Model):
    class Meta:
        app_label = 'test_app'

    name = models.CharField(max_length=50)


class TestPage(TranslationMixin, Page):
    class Meta:
        app_label = 'test_app'

    name = models.CharField(max_length=50)
