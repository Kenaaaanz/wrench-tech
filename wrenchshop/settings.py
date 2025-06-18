from pathlib import Path

import os
import requests
from requests.auth import HTTPBasicAuth

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3%y3laftm62q0zaj+s7#p-xqq9(&#q+)s8)p-&#&bz*0$!xu$0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

#CSRF_TRUSTED_ORIGINS = ['https://wrenchshop.onrender.com']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'store',
    'whitenoise',
    'mpesa',
    'mpesa_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wrenchshop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_preprocessors.store_menu',
                'store.context_preprocessors.cart_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'wrenchshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',

     'default': {
         #'ENGINE': 'django.db.backends.sqlite3',
         #'NAME': BASE_DIR / 'db.sqlite3',
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "wrench-tech",
        "USER": "postgres",
        "PASSWORD": "Ken@4427",
        "HOST": "localhost",
        "PORT": "5432",


    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'wrenchshop/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static') # Automatically Created on Production

# Settings for Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MPESA_CONSUMER_KEY = 'f005bZS0zNCR6uvH2CQ8PMDpAQysRlpDCBA4Y4YKjaJ6TDzY'
MPESA_CONSUMER_SECRET = 'XD0bH0OyzlF6pT99j9Ao8x0RYEIoEziyXArbGcWHjmTROwVGGBhPybG5iCFpruLi'
MPESA_SHORTCODE = '174379'  
MPESA_PASSKEY = 'mBIhoeGZREI468D2y/EaY81Reh+Jbgs+ZtPxH2lPyY24sxXTopY4G0HoQtEB+18f3yTUk5vE7qGmyqrNkly5kBfF52Ey9JHZymCJaSSb5qIsOwobNS1g45knm8Ocu4CtqRiVeuFHeSDKl+ZA5yxTq3wKNqT51fHD8JcGYDkZkGUy//M+qgaIwgPBmX/CD7G+NHvgH/pAplh+sAn+fVjEnSr+hT6AVcgejSW/3c+uXMWaOwqC5wiVsluNU8zqHP6pYDwIHkQV2tKSnSQ0EsgBRDuy/PuS74RrpFxqVvJMgtCp3yMyham6bTUjZH+dBAA/R/OZwTM6xbRzxuyrmEXSpw=='
MPESA_CALLBACK_URL = 'https://127.0.0.1/mpesa/callback/'

# Define the base URL for the MPESA API
MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke'

# Example: Generate M-Pesa access token and use it for STK Push
def get_mpesa_access_token():
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    access_token = response.json().get('access_token')
    return access_token

def make_stk_push():
    access_token = get_mpesa_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        # ... your STK Push payload here ...
    }
    url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
