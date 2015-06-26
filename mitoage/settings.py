""" ================= General settings ================= """
import os

import dj_database_url
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.core.urlresolvers import reverse


ADMINS = ( ('Robi Tacutu', 'robi.tacutu@gmail.com'), )
MANAGERS = ADMINS

# Time zone and internationalization
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Site info
SITE_ID = 1

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q1*s(h7_&c*50$4@ek5vr=a#$%*c5!p#(vkz3o#&g9iefh!#6t'

# SECURITY WARNING: don't run with debug turned on in production!
""" ================= DEBUG mode? ================= """
#DEBUG = True if (os.environ['DEBUG'].lower())=='true' else False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['mitoage.org', 'mitoage.info', 'mitoage.herokuapp.com', 'localhost', '127.0.0.1']

ROOT_URLCONF = 'mitoage.urls'
WSGI_APPLICATION = 'mitoage.wsgi.application'


""" ================= static and media files ================= """
STATIC_ROOT = 'static_collected_files'
STATIC_URL = '/static/'
#STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'static_collected_files'), )
#STATICFILES_DIRS = ( os.path.join('static_collected_files'), )


""" ================= project packages and middleware ================= """
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our packages:
    'mitoage',
    'mitoage.static_pages',
    'mitoage.taxonomy',
    'mitoage.analysis',

    # Admin:
    'suit',
    'django.contrib.admin',
    #'django.contrib.admindocs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)



""" ================= Template loaders & directories ================= """

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates'), 
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',   # needed for django-suit!
)



""" ================= Database ================= """
DATABASES = {
    'default': {
        'ENGINE': '', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
""" !!!Parse database configuration from $DATABASE_URL (settings made with dj-database-url """
DATABASES['default'] = dj_database_url.config(default=os.environ['DATABASE_URL'])   # don't forget to set the DATABASE_URL in your




""" ================= Admin - suit configuration ================= """
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': "MitoAge - the admin",
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i',

    # forms
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    'MENU_ICONS': {
        'sites': 'icon-leaf',
        'auth': 'icon-lock',
    },
    'MENU_OPEN_FIRST_CHILD': True, # Default True
    'MENU': (
        {'label': 'Back to website', 'icon':'icon-heart', 'url': '/'},
        {'app': 'sites', 'label': 'Sites & settings', 'icon':'icon-cog', 'models': (
            'site',
        )},
        {'app': 'auth', 'label': 'Authentication', 'icon':'icon-lock', 'models': (
            'auth.user', 'auth.group', 
        )},
        {'app': 'taxonomy', 'label': 'Taxonomy', 'icon':'icon-leaf', 'models': (
            'taxonomy.taxonomyspecies', 'taxonomy.taxonomyfamily', 'taxonomy.taxonomyorder', 'taxonomy.taxonomyclass', 
            {'url': 'admin:taxonomy_csvimport', 'label': 'Import taxonomy'},
        )},
        {'label': 'Lifespan@AnAge', 'icon':'icon-tag', 'url': 'admin:anage_csvimport'},
        {'app': 'analysis', 'label': 'MitoAge', 'icon':'icon-star', 'models': (
            'analysis.mitoageentry',  
            {'url': 'admin:bc_csvimport', 'label': 'Import base composition'},
            {'url': 'admin:cu_csvimport', 'label': 'Import codon usage'},
        )},
        {'label': 'Future ToDOs', 'icon':'icon-list-alt', 'url': 'admin:todo_list'},
    ),
    # misc
    'LIST_PER_PAGE': 15
}
