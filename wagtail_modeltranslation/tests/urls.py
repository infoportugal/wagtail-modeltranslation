from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

from wagtail.core import urls as wagtail_urls

urlpatterns = [
    url(r'^set_language/$', set_language, {}, name='set_language'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    url(r'', include(wagtail_urls)),
)
