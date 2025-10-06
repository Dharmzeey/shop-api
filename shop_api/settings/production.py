from .base import *
from dotenv import load_dotenv
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')

# CORS_ALLOWED_ORIGINS = ['https://shop.dharmzeey.com', 'http://localhost:3000']

CSRF_TRUSTED_ORIGINS = ['https://shop-api.dharmzeey.com']

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    'PORT': os.getenv('DB_PORT'),
  }
}

CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'shop_cache_table',
    },
  'password_reset': {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'password_reset_cache_table',
  },
  'email_verification': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'email_verification_cache_table',
    },
  'password_tries': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'password_tries_cache_table',
    },
  'password_attempts': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'password_attempts_cache_table',
    },
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


# payment
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/html/staticfiles'
# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# MEDIA_URL = 'media/'
# MEDIA_ROOT = '/var/www/html/mediafiles'

AWS_ACCESS_KEY_ID = os.environ.get('B2_APPLICATION_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('B2_APPLICATION_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('B2_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('B2_REALM', 'eu-central-003')


AWS_S3_ENDPOINT_URL = f'https://s3.{AWS_S3_REGION_NAME}.backblazeb2.com'

# Optional: if you want to serve via Cloudflare later
AWS_S3_CUSTOM_DOMAIN = "media.dharmzeey.com"

# If you want uploads inside "media/"
AWS_LOCATION = "media"

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}