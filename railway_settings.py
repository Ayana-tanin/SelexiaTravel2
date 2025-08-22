# Railway Production Settings
# Скопируйте эти настройки в .env файл на Railway

# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,*.up.railway.app

# Database - Railway PostgreSQL
DATABASE_NAME=selexia_travel_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-postgres-password
DATABASE_HOST=postgres.railway.internal
DATABASE_PORT=5432
DATABASE_ENGINE=railway

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selexiatravelauth@gmail.com
EMAIL_HOST_PASSWORD=afjs pirk rdtg tqyw
DEFAULT_FROM_EMAIL=selexiatravelauth@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Site Settings
SITE_ID=1

# Railway Environment
RAILWAY_ENVIRONMENT=production
RAILWAY_STATIC_URL=/static/
RAILWAY_MEDIA_URL=/media/
