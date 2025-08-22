# Быстрый запуск Gmail интеграции

## Для пользователя tanRan.an@yandex.ru

### Что получит пользователь:
- Автоматическое обновление имени и фамилии из Gmail
- Синхронизация email адреса
- Управление подключением через dashboard

## Быстрая настройка (5 минут)

### 1. Установка зависимостей
```bash
pip install -r gmail_requirements.txt
```

### 2. Создание Google Cloud проекта
1. Перейти на [console.cloud.google.com](https://console.cloud.google.com/)
2. Создать новый проект "SELEXIA Travel"
3. Включить Gmail API
4. Создать OAuth 2.0 credentials
5. Скачать `credentials.json`

### 3. Настройка Django
В `settings.py` добавить:
```python
GMAIL_CLIENT_ID = 'ваш-client-id.apps.googleusercontent.com'
GMAIL_CLIENT_SECRET = 'ваш-client-secret'
GMAIL_CREDENTIALS_FILE = 'credentials.json'
```

### 4. Применение миграций
```bash
python manage.py migrate
```

### 5. Размещение файлов
- `credentials.json` → корень проекта
- `gmail_settings.py` → корень проекта

## Тестирование

### 1. Создать пользователя
```python
# В Django shell
from selexia_travel.models import User
user = User.objects.create_user(
    email='tanRan.an@yandex.ru',
    password='testpass123'
)
```

### 2. Проверить работу
1. Войти под пользователем
2. Перейти в `/dashboard/`
3. Нажать "Подключить Gmail"
4. Пройти OAuth авторизацию
5. Проверить обновление профиля

## URL маршруты

- `/gmail/connect/` - подключение Gmail
- `/gmail/callback/` - OAuth callback
- `/gmail/sync/` - синхронизация профиля
- `/gmail/disconnect/` - отключение Gmail

## Возможные проблемы

### Ошибка "Invalid Credentials"
- Проверить правильность CLIENT_ID и CLIENT_SECRET
- Убедиться, что credentials.json актуален

### Ошибка "Access Denied"
- Проверить включен ли Gmail API
- Проверить redirect URIs в Google Cloud Console

### Токен не обновляется
- Проверить наличие refresh_token
- Проверить логи Django

## Готово!

После настройки пользователь `tanRan.an@yandex.ru` сможет:
1. Подключить Gmail аккаунт
2. Автоматически получить имя и фамилию
3. Управлять подключением через dashboard
