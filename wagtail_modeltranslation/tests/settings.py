"""
Settings overrided for test time
"""
import os

DEBUG = False

LOGGING_CONFIG = None

# Choose database for settings
test_db = os.environ.get('DB', 'sqlite')
test_db_host = os.getenv('DB_HOST', 'localhost')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
if test_db == 'mysql':
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'wagtail_modeltranslation'),
        'USER': os.getenv('MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'password'),
        'HOST': test_db_host,
    })
elif test_db == 'postgres':
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_DB', 'postgres'),
        'NAME': os.getenv('POSTGRES_DB', 'wagtail_modeltranslation'),
        'HOST': test_db_host,
    })

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    'wagtail.contrib.simple_translation',
    'wagtail.contrib.styleguide',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.frontend_cache',
    'wagtail.contrib.search_promotions',
    'wagtail.contrib.settings',
    'wagtail.contrib.table_block',
    'wagtail.contrib.forms',

    'wagtail.search',
    'wagtail.embeds',
    'wagtail.images',
    'wagtail.sites',
    'wagtail.locales',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.admin',
    'wagtail.api.v2',
    'wagtail',

    'taggit',
    'rest_framework',

    'wagtail_modeltranslation',
    'wagtail_modeltranslation.makemigrations',
    'wagtail_modeltranslation.migrate',

    'wagtail_modeltranslation.tests',
]

LANGUAGES = (('de', 'Deutsch'),
             ('en', 'English'))
LANGUAGE_CODE = 'de'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'de'

USE_I18N = True
USE_TZ = False
MIDDLEWARE_CLASSES = ()

MODELTRANSLATION_AUTO_POPULATE = False
MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': (MODELTRANSLATION_DEFAULT_LANGUAGE,)}
# MODELTRANSLATION_FALLBACK_LANGUAGES = ()

ROOT_URLCONF = 'wagtail_modeltranslation.tests.urls'

TRANSLATE_SLUGS = True

SECRET_KEY = 'not important'

ALLOWED_HOSTS = ['localhost']

WAGTAILADMIN_BASE_URL = 'http://localhost'
