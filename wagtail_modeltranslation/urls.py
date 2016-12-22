# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from wagtail.wagtailadmin import urls as wagtailadmin_urls

from wagtail_modeltranslation.patch_wagtailadmin_views import new_copy

urlpatterns = [
    url(r'^pages/(\d+)/copy/$', new_copy, name = 'copy'),
    url(r'^', include(wagtailadmin_urls)),
]
