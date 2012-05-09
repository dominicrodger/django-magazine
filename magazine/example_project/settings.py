import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ID = 1
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))
MEDIA_URL = STATIC_URL + "media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))
ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)
SECRET_KEY = "incrediblysecretkeyyoushouldchange"
ADMINS = ()
MANAGERS = ADMINS
LOGIN_URL = "/admin/"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'tinymce',
    'magazine',
)


TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'relative_urls': False,
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_buttons1': ("bold,italic,separator,bullist,numlist,"
                                "separator,blockquote,separator,link,unlink,"
                                "separator,image,separator,pasteword,cleanup,"
                                "code"),
    'theme_advanced_buttons2': "",
    'theme_advanced_buttons3': "",
    'plugins': "paste",
}
