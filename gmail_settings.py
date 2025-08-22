"""
Настройки для Gmail API интеграции
"""

# Gmail API настройки
GMAIL_CLIENT_ID = 'your-gmail-client-id.apps.googleusercontent.com'
GMAIL_CLIENT_SECRET = 'your-gmail-client-secret'

# Файлы для OAuth
GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_FILE = 'token.json'

# Области доступа
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]

# Настройки токенов
GMAIL_TOKEN_EXPIRY_HOURS = 1

# Настройки синхронизации
GMAIL_SYNC_INTERVAL_HOURS = 24
GMAIL_MAX_MESSAGES = 10

# Настройки безопасности
GMAIL_REQUIRE_VERIFIED_EMAIL = True
GMAIL_ALLOW_REFRESH_TOKEN = True

# Настройки логирования
GMAIL_LOG_LEVEL = 'INFO'
GMAIL_LOG_FILE = 'gmail_integration.log'

# Настройки ошибок
GMAIL_MAX_RETRIES = 3
GMAIL_RETRY_DELAY_SECONDS = 5

# Настройки профиля
GMAIL_UPDATE_NAME = True
GMAIL_UPDATE_EMAIL = True
GMAIL_UPDATE_PICTURE = False  # Пока отключено для безопасности

# Настройки уведомлений
GMAIL_SEND_NOTIFICATIONS = True
GMAIL_NOTIFICATION_EMAIL = 'admin@selexiatravel.com'

# Настройки тестирования
GMAIL_TEST_MODE = False
GMAIL_TEST_USER_EMAIL = 'test@example.com'

# Инструкции по настройке:
"""
1. Создайте проект в Google Cloud Console
2. Включите Gmail API
3. Создайте OAuth 2.0 credentials
4. Скачайте credentials.json и поместите в корень проекта
5. Добавьте разрешенные redirect URIs:
   - http://localhost:8000/gmail/callback/ (для разработки)
   - https://yourdomain.com/gmail/callback/ (для продакшена)
6. Обновите GMAIL_CLIENT_ID и GMAIL_CLIENT_SECRET в этом файле
7. Добавьте эти настройки в settings.py Django проекта

Пример добавления в settings.py:
from .gmail_settings import *

# Или импортируйте конкретные настройки:
# from .gmail_settings import GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET
"""
