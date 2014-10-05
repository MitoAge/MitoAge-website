""" ================= General settings ================= """
ADMINS = (
    ('Robi Tacutu', 'robi.tacutu@gmail.com'), ('Bogdan Dinu', 'bogdan.dinu@gmail.com'),
)
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
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q1*s(h7_&c*50$4@ek5vr=a#$%*c5!p#(vkz3o#&g9iefh!#6t'

# SECURITY WARNING: don't run with debug turned on in production!
""" ================= DEBUG mode? ================= """
DEBUG = True if (os.environ['DEBUG'].lower())=='true' else False
TEMPLATE_DEBUG = DEBUG


ALLOWED_HOSTS = []

ROOT_URLCONF = 'virtual_character.urls'
WSGI_APPLICATION = 'virtual_character.wsgi.application'


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
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

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
import dj_database_url
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
    'ADMIN_NAME': "Virtual Character - the admin",
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
        {'app': 'sites', 'label': 'Sites & settings', 'icon':'icon-leaf', 'models': (
            'site',
        )},
        {'app': 'auth', 'label': 'Authentication', 'icon':'icon-lock', 'models': (
            'auth.user', 'auth.group', 
        )},
    ),
    # misc
    'LIST_PER_PAGE': 15
}

''' Below is the configuration from Trust me, I'm a biologist - needs to be adapted
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': "Trust me, I'm a biologist - the admin",
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i',

    # forms
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    #'SEARCH_URL': '/admin/auth/user/',
    'MENU_ICONS': {
        'sites': 'icon-leaf',
        'auth': 'icon-lock',
    },
    #'MENU_OPEN_FIRST_CHILD': False, # Default True
    #'MENU_EXCLUDE': ('auth.group',),
    'MENU': (
        {'label': 'Back to website', 'icon':'icon-heart', 'url': '/'},
        '-', 
        {'app': 'sites', 'label': 'Sites & settings', 'icon':'icon-leaf', 'models': (
            {'label':'Trust me websites', 'model':'site'}, 'website.faq', 'website.websitesuggestion'
        )},
        {'app': 'auth', 'label': 'Authentication', 'icon':'icon-lock', 'models': (
            'auth.user', 'auth.group', 'avatar.avatar', 
            'account.emailaddress', 'account.emailconfirmation',  
            'socialaccount.socialapp', 'socialaccount.socialaccount', 'socialaccount.socialtoken', 
            'openid.openidnonce', 'openid.openidstore'
        )},
        '-', 
        
        {'app': 'photologue', 'label': 'Pictures & galleries', 'icon':'icon-picture', 'models': (
            'photologue.photo', 'photologue.gallery', 'photologue.photoeffect', 'photologue.photosize', 'photologue.watermark', 
            'tagging.tag', 'tagging.taggeditem' 
        )},
        {'app': 'photologue_hack', 'label': 'Pictures - advanced', 'icon':'icon-camera', 'models': (
            {'label':'Gallery upload', 'model':'photologue_hack.improvedgalleryupload'}, 
            {'label':'Picture scores', 'model':'photologue_hack.photovotescore'}, 
            {'label':'Picture metadata', 'model':'photologue_hack.photometadata'}, 
            {'label':'Favorite pictures', 'model':'photologue_hack.userphotofavoriterelationship'}, 
            {'label':'User votes', 'model':'photologue_hack.userphotovoterelationship'}, 
        )},
        
        '-', 
        {'app': 'publishing', 'label': 'Publishing system', 'icon':'icon-share'},
        {'app': 'schedule', 'label': 'Scheduling', 'icon':'icon-calendar'},
        {'app': 'djcelery', 'label': 'Celery', 'icon':'icon-tasks'},

        '-', 
        {'app':'debugging', 'label': 'Debug', 'icon':'icon-cog'},

        # Custom app and model with permissions
        #{'label': 'Secure', 'permissions': 'auth.add_user', 'models': [
        #    {'label': 'custom-child', 'permissions': ('auth.add_user', 'auth.add_group')}
        #]},
    ),
    # misc
    'LIST_PER_PAGE': 15
}'''