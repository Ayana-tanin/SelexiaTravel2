# coding: utf-8
import os
from pathlib import Path
from django.contrib.messages import constants as messages
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.vk',
    'allauth.socialaccount.providers.mailru',
    'allauth.socialaccount.providers.yandex',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'selexia_travel',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'selexia_travel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'selexia_travel.context_processors.site_context',  # Временно отключен для отладки
            ],
        },
    },
]

WSGI_APPLICATION = 'selexia_travel.wsgi.application'

# Database Configuration
# Приоритет подключения к PostgreSQL через .env файл
if config('DATABASE_URL', default=''):
    # Основной способ подключения через DATABASE_URL
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Дополнительные настройки для PostgreSQL
    if 'postgresql' in config('DATABASE_URL'):
        DATABASES['default']['OPTIONS'] = {
            'connect_timeout': 10,
            'sslmode': 'require',
            'application_name': 'selexia_travel',
        }
    
    print("🔍 Подключение к БД через DATABASE_URL")
    
elif (config('DB_ENGINE', default='') == 'postgresql' or 
      config('DB_ENGINE', default='') == 'postgres' or
      config('DB_NAME', default='') and config('DB_USER', default='') and config('DB_PASSWORD', default='')):
    # Подключение через отдельные переменные окружения
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 10,
                'sslmode': config('DB_SSL_MODE', default='prefer'),
                'application_name': 'selexia_travel',
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
    print("🔍 Подключение к PostgreSQL через переменные окружения")
else:
    # Fallback на SQLite для разработки
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("🔍 Использование SQLite для разработки")

# Логирование настроек базы данных
print(f"🔍 Настройки БД:")
print(f"   DATABASE_URL: {'Установлен' if config('DATABASE_URL', default='') else 'Не установлен'}")
print(f"   DB_ENGINE: {config('DB_ENGINE', default='Не установлен')}")
print(f"   DB_NAME: {config('DB_NAME', default='Не установлен')}")
print(f"   DB_HOST: {config('DB_HOST', default='Не установлен')}")
print(f"   DB_PORT: {config('DB_PORT', default='Не установлен')}")
print(f"   Текущий ENGINE: {DATABASES['default']['ENGINE']}")

# Дополнительные настройки PostgreSQL
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    # Оптимизация для PostgreSQL
    DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'connect_timeout': 10,
        'sslmode': 'require',
        'application_name': 'selexia_travel',
    })
    
    # Настройки пула соединений
    DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 минут
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
    
    print("🔧 PostgreSQL оптимизации применены")
    print(f"   CONN_MAX_AGE: {DATABASES['default']['CONN_MAX_AGE']} секунд")
    print(f"   SSL Mode: {DATABASES['default']['OPTIONS'].get('sslmode', 'default')}")
    print(f"   Connect Timeout: {DATABASES['default']['OPTIONS'].get('connect_timeout', 'default')} секунд")
    
    # Дополнительная информация о подключении
    db_info = DATABASES['default']
    print(f"🔍 Информация о подключении:")
    print(f"   Хост: {db_info.get('HOST', 'N/A')}")
    print(f"   Порт: {db_info.get('PORT', 'N/A')}")
    print(f"   База данных: {db_info.get('NAME', 'N/A')}")
    print(f"   Пользователь: {db_info.get('USER', 'N/A')}")
else:
    print("🔍 SQLite база данных - PostgreSQL оптимизации не применяются")

# Password validation
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
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'static/dist',  # Vue.js сборка
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1

# Vue.js настройки
VUE_APP_TITLE = 'SELEXIA Travel'
VUE_APP_API_URL = '/api/'
VUE_APP_DEBUG = DEBUG

# REST Framework настройки
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS настройки для Vue.js
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3002",  # Vue.js dev server
    "http://127.0.0.1:3002",
    "http://localhost:8000",  # Django dev server
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# API настройки
API_VERSION = 'v1'
API_BASE_URL = f'/api/{API_VERSION}/'

# Cache настройки
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session настройки
SESSION_COOKIE_AGE = 86400 * 30  # 30 дней
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF настройки
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3002',
    'http://127.0.0.1:3002',
]

# Authentication
AUTH_USER_MODEL = 'selexia_travel.User'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Django Allauth settings для Django 4.2+
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SIGNUP_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGIN_REDIRECT_URL = '/dashboard/'

# Socialaccount behavior
SOCIALACCOUNT_LOGIN_ON_GET = True

# Настройки для кастомной модели User
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'  # Указываем поле username
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Social Auth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'APP': {
            'client_id': config('FACEBOOK_APP_ID', default=''),
            'secret': config('FACEBOOK_APP_SECRET', default=''),
        },
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'ru_RU',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    },
    'yandex': {
        'APP': {
            'client_id': config('YANDEX_CLIENT_ID', default=''),
            'secret': config('YANDEX_CLIENT_SECRET', default=''),
        },
        'SCOPE': ['login:info', 'login:email'],
        'AUTH_PARAMS': {'force_confirm': 'true'},
        'LOCALE_FUNC': lambda request: 'ru_RU',
    }
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Email settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@selexiatravel.com')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    print(f"🔒 Продакшен настройки безопасности: АКТИВНЫ")
else:
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    print(f"🔓 Локальные настройки безопасности")

# Railway настройки - улучшенное определение окружения
RAILWAY_ENVIRONMENT = (
    config('DATABASE_URL', default='').startswith('postgresql://') and 
    ('railway' in config('DATABASE_URL', default='') or 'rlwy.net' in config('DATABASE_URL', default=''))
) or config('RAILWAY_ENVIRONMENT', default=False, cast=bool)

if RAILWAY_ENVIRONMENT:
    print("🚂 Railway окружение: АКТИВНО")
    
    # Обновляем ALLOWED_HOSTS для Railway
    ALLOWED_HOSTS = [
        'selexiatravel2.up.railway.app',
        '*.up.railway.app',
        '*.rlwy.net',
        'localhost',
        '127.0.0.1'
    ]
    
    # Обновляем CSRF_TRUSTED_ORIGINS для Railway
    CSRF_TRUSTED_ORIGINS = [
        'https://selexiatravel2.up.railway.app',
        'https://*.up.railway.app',
        'https://*.rlwy.net'
    ]
    
    # Обновляем CORS настройки для Railway
    CORS_ALLOWED_ORIGINS = [
        'https://selexiatravel2.up.railway.app',
        'https://*.up.railway.app',
        'https://*.rlwy.net',
        'http://localhost:3002',
        'http://127.0.0.1:3002',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]
    
    # Настройки безопасности для Railway
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False  # Нужно для JavaScript
    SESSION_COOKIE_HTTPONLY = True
    
    print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"   CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
    print(f"   CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
else:
    print("🏠 Локальное окружение")
    print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"   CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
    print(f"   CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Gmail API настройки
GMAIL_CLIENT_ID = config('GMAIL_CLIENT_ID', default='your-gmail-client-id.apps.googleusercontent.com')
GMAIL_CLIENT_SECRET = config('GMAIL_CLIENT_SECRET', default='your-gmail-client-secret')
GMAIL_CREDENTIALS_FILE = config('GMAIL_CREDENTIALS_FILE', default='credentials.json')
GMAIL_TOKEN_FILE = config('GMAIL_TOKEN_FILE', default='token.json')

# Проверка критических переменных окружения
print(f"🔍 Проверка переменных окружения:")
print(f"   SECRET_KEY: {'Установлен' if config('SECRET_KEY', default='') != 'django-insecure-your-secret-key-here-change-this' else 'НЕ ИЗМЕНЕН'}")
print(f"   DEBUG: {DEBUG}")
print(f"   DB_ENGINE: {config('DB_ENGINE', default='Не установлен')}")
print(f"   EMAIL_HOST: {config('EMAIL_HOST', default='Не установлен')}")
print(f"   GOOGLE_CLIENT_ID: {'Установлен' if config('GOOGLE_CLIENT_ID', default='') else 'Не установлен'}")
print(f"   YANDEX_CLIENT_ID: {'Установлен' if config('YANDEX_CLIENT_ID', default='') else 'Не установлен'}")
print("=" * 60)

# Дополнительные настройки PostgreSQL
if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    # Оптимизация для PostgreSQL
    DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {})
    DATABASES['default']['OPTIONS'].update({
        'connect_timeout': 10,
        'sslmode': 'require',
        'application_name': 'selexia_travel',
    })
    
    # Настройки пула соединений
    DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 минут
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
    
    print("🔧 PostgreSQL оптимизации применены")
    print(f"   CONN_MAX_AGE: {DATABASES['default']['CONN_MAX_AGE']} секунд")
    print(f"   SSL Mode: {DATABASES['default']['OPTIONS'].get('sslmode', 'default')}")
    print(f"   Connect Timeout: {DATABASES['default']['OPTIONS'].get('connect_timeout', 'default')} секунд")
    
    # Дополнительная информация о подключении
    db_info = DATABASES['default']
    print(f"🔍 Информация о подключении:")
    print(f"   Хост: {db_info.get('HOST', 'N/A')}")
    print(f"   Порт: {db_info.get('PORT', 'N/A')}")
    print(f"   База данных: {db_info.get('NAME', 'N/A')}")
    print(f"   Пользователь: {db_info.get('USER', 'N/A')}")
else:
    print("🔍 SQLite база данных - PostgreSQL оптимизации не применяются")

# Дополнительные настройки безопасности для Railway
if RAILWAY_ENVIRONMENT:
    print("🔒 Railway настройки безопасности применены")