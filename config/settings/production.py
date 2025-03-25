from .base import *
import os
import sys
import dj_database_url
import logging

# Print debug info to console
SECRET_KEY = os.getenv("SECRET_KEY", "3e041fd6d542e904b56b6d65b40a71dff8ebdcd90850f4af5c99655acb5dbce5")
print("LOADING PRODUCTION SETTINGS")
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Environment variables:", [(k, v[:10] + '...' if len(v) > 10 else v) for k, v in os.environ.items() if k in ('DJANGO_SETTINGS_MODULE', 'DATABASE_URL', 'DEBUG', 'ALLOWED_HOSTS')])

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()],
)

# Allow debug mode in production only if explicitly set
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Use environment variables or fallback to hardcoded values for Railway
ALLOWED_HOSTS = ["web-production-f2a6e.up.railway.app"]
logging.info(f"ALLOWED_HOSTS set to: {ALLOWED_HOSTS}")

# CSRF and CORS settings
CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if not host.startswith('localhost') and not host.startswith('127.0.0.1')]
if not CSRF_TRUSTED_ORIGINS:
    # Add default Railway domain
    CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']

# Optionally disable HTTPS redirect in certain environments

SECURE_SSL_REDIRECT = False  # Set to False to prevent redirect loop
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Add this if behind a proxy

SECURE_BROWSER_XSS_FILTER = True

# Configure static files
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Database configuration

database_url = os.environ.get('DATABASE_URL')
if database_url:
    logging.info(f"Configuring database with DATABASE_URL (masked: {database_url[:15]}...)")
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    logging.warning("No DATABASE_URL found, using SQLite as fallback")
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Disable email settings if not configured
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
if not (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
    logging.warning("Email settings not configured, using console backend")
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if not DEBUG:  # Ensure media files work in production
    import mimetypes
    mimetypes.add_type("image/png", ".png", True)
    mimetypes.add_type("image/jpeg", ".jpg", True)
    mimetypes.add_type("image/jpeg", ".jpeg", True)
    mimetypes.add_type("image/gif", ".gif", True)
    mimetypes.add_type("image/webp", ".webp", True)
    mimetypes.add_type("image/svg+xml", ".svg", True)
    mimetypes.add_type("image/svg+xml", ".svgz", True)
    mimetypes.add_type("image/tiff", ".tiff", True)
    mimetypes.add_type("image/tiff", ".tif", True)
    mimetypes.add_type("image/tiff", ".tiff", True)
    mimetypes.add_type("image/tiff", ".tif", True)