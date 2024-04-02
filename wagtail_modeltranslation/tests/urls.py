from django.urls import include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

from wagtail import urls as wagtail_urls

urlpatterns = [
    re_path(r"^set_language/$", set_language, {}, name="set_language"),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    re_path(r"", include(wagtail_urls)),
)
