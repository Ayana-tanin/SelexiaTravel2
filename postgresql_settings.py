# PostgreSQL Production Settings
# Скопируйте эти настройки в .env файл

# Database - PostgreSQL
DATABASE_URL=postgresql://selexia_user:selexia_password@localhost:5432/selexia_travel_db
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=selexia_travel_db
DATABASE_USER=selexia_user
DATABASE_PASSWORD=selexia_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Production Security Settings
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,selexiatravel.com,www.selexiatravel.com
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Settings (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selexiatravelauth@gmail.com
EMAIL_HOST_PASSWORD=afjs pirk rdtg tqyw
DEFAULT_FROM_EMAIL=selexiatravelauth@gmail.com

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# AWS S3 (опционально)
# AWS_ACCESS_KEY_ID=your-aws-access-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=your-region
# AWS_S3_CUSTOM_DOMAIN=your-domain
