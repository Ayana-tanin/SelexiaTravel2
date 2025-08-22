# Настройка входа через Google OAuth

## Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API:
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google+ API" и включите его
   - Также включите "Google Identity" API

## Шаг 2: Создание OAuth 2.0 приложения

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth 2.0 Client IDs"
3. Выберите тип приложения "Web application"
4. Заполните форму:
   - **Name**: SelexiaTravel
   - **Authorized JavaScript origins**:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - **Authorized redirect URIs**:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/`
     - `http://127.0.0.1:8000/accounts/google/login/`

5. Нажмите "Create"
6. Скопируйте **Client ID** и **Client Secret**

## Шаг 3: Настройка переменных окружения

Создайте файл `.env` в корне проекта (если его нет) и добавьте:

```env
GOOGLE_CLIENT_ID=ваш-client-id-здесь
GOOGLE_CLIENT_SECRET=ваш-client-secret-здесь
```

## Шаг 4: Настройка базы данных

1. Выполните миграции:
```bash
python manage.py migrate
```

2. Создайте суперпользователя (если еще не создан):
```bash
python manage.py createsuperuser
```

## Шаг 5: Настройка сайта в админке

1. Запустите сервер:
```bash
python manage.py runserver
```

2. Перейдите в админку: `http://localhost:8000/admin/`
3. Войдите как суперпользователь
4. Перейдите в "Sites" → "Sites"
5. Отредактируйте сайт с ID=1:
   - **Domain name**: `localhost:8000`
   - **Display name**: `SelexiaTravel`

## Шаг 6: Настройка Google OAuth приложения

1. В админке перейдите в "Social Applications" → "Social applications"
2. Нажмите "Add social application"
3. Заполните форму:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: ваш Google Client ID
   - **Secret key**: ваш Google Client Secret
   - **Sites**: выберите `localhost:8000`

## Шаг 7: Тестирование

1. Перейдите на страницу входа: `http://localhost:8000/accounts/login/`
2. Нажмите кнопку "Google"
3. Должно произойти перенаправление на Google для авторизации
4. После успешной авторизации вы будете перенаправлены обратно на сайт

## Возможные проблемы и решения

### Ошибка "Invalid redirect_uri"
- Убедитесь, что URI перенаправления в Google Cloud Console точно совпадают с теми, что используются в Django
- Проверьте, что нет лишних слешей в конце

### Ошибка "Client ID not found"
- Проверьте, что GOOGLE_CLIENT_ID правильно указан в .env файле
- Убедитесь, что .env файл загружается (проверьте python-decouple)

### Ошибка "Site matching query does not exist"
- Убедитесь, что сайт с ID=1 существует в базе данных
- Проверьте настройки SITE_ID в settings.py

## Настройка для продакшена

При развертывании на продакшене:

1. Обновите URI перенаправления в Google Cloud Console:
   - `https://ваш-домен.com/accounts/google/login/callback/`
   - `https://ваш-домен.com/accounts/google/login/`

2. Обновите настройки в Django:
   - Установите `DEBUG = False`
   - Обновите `ALLOWED_HOSTS`
   - Включите HTTPS: `SECURE_SSL_REDIRECT = True`

3. Обновите настройки сайта в админке:
   - Domain name: `ваш-домен.com`

## Дополнительные настройки

### Настройка разрешений для Google OAuth
В `settings.py` можно настроить дополнительные параметры:

```python
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
}
```

### Настройка автоматического создания пользователей
По умолчанию django-allauth автоматически создает пользователей при входе через социальные сети. Если нужно изменить это поведение, добавьте в `settings.py`:

```python
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```
