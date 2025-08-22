# Gmail интеграция для SELEXIA Travel

## Описание

Система интеграции с Gmail API позволяет пользователям автоматически обновлять свой профиль данными из Gmail аккаунта. Пользователь `tanRan.an@yandex.ru` сможет подключить свой Gmail аккаунт и автоматически получить имя и другие данные профиля.

## Основные возможности

### 1. Автоматическое обновление профиля
- Имя и фамилия из Gmail профиля
- Email адрес (если отличается)
- Дата последнего обновления профиля

### 2. Безопасность
- Доступ только к базовой информации профиля
- Нет доступа к содержимому писем
- OAuth 2.0 аутентификация
- Автоматическое обновление токенов

### 3. Управление подключением
- Подключение Gmail аккаунта
- Синхронизация профиля
- Отключение аккаунта
- Статус подключения в dashboard

## Установка и настройка

### 1. Требования
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Настройка Google Cloud Console

#### Шаг 1: Создание проекта
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Gmail API в разделе "APIs & Services" > "Library"

#### Шаг 2: Создание OAuth 2.0 credentials
1. Перейдите в "APIs & Services" > "Credentials"
2. Нажмите "Create Credentials" > "OAuth 2.0 Client IDs"
3. Выберите тип приложения "Web application"
4. Добавьте разрешенные redirect URIs:
   - `http://localhost:8000/gmail/callback/` (для разработки)
   - `https://yourdomain.com/gmail/callback/` (для продакшена)
5. Скачайте файл `credentials.json`

#### Шаг 3: Размещение файла
Поместите `credentials.json` в корень проекта Django.

### 3. Настройка Django

#### Обновите settings.py:
```python
# Gmail API настройки
GMAIL_CLIENT_ID = 'your-client-id.apps.googleusercontent.com'
GMAIL_CLIENT_SECRET = 'your-client-secret'
GMAIL_CREDENTIALS_FILE = 'credentials.json'
GMAIL_TOKEN_FILE = 'token.json'
```

#### Или импортируйте из gmail_settings.py:
```python
from .gmail_settings import *
```

### 4. Применение миграций
```bash
python manage.py migrate
```

## Использование

### 1. Подключение Gmail аккаунта
1. Пользователь заходит в личный кабинет (`/dashboard/`)
2. Нажимает кнопку "Подключить Gmail"
3. Перенаправляется на страницу авторизации Google
4. Разрешает доступ к профилю
5. Возвращается в dashboard с подключенным аккаунтом

### 2. Синхронизация профиля
- Автоматическая при подключении
- Ручная через кнопку "Синхронизировать"
- Периодическая (можно настроить через cron)

### 3. Отключение Gmail
- Через кнопку "Отключить" в dashboard
- Все данные Gmail удаляются из профиля

## Структура файлов

```
selexia_travel/
├── models.py                 # Обновленная модель User с полями Gmail
├── views.py                  # Views для Gmail интеграции
├── gmail_integration.py      # Основная логика Gmail API
├── admin.py                  # Обновленная админка
└── migrations/
    └── 0007_add_gmail_fields.py

templates/users/
├── dashboard.html            # Обновленный dashboard с Gmail статусом
└── connect_gmail.html        # Страница подключения Gmail

gmail_settings.py             # Настройки Gmail API
```

## API Endpoints

### Подключение Gmail
- **URL**: `/gmail/connect/`
- **Метод**: POST
- **Описание**: Начинает процесс OAuth авторизации

### Callback Gmail
- **URL**: `/gmail/callback/`
- **Метод**: GET
- **Описание**: Обрабатывает ответ от Google OAuth

### Синхронизация профиля
- **URL**: `/gmail/sync/`
- **Метод**: POST
- **Описание**: Обновляет профиль из Gmail

### Отключение Gmail
- **URL**: `/gmail/disconnect/`
- **Метод**: POST
- **Описание**: Отключает Gmail аккаунт

## Модель данных

### Новые поля в User:
```python
gmail_access_token = models.TextField(blank=True, null=True)
gmail_refresh_token = models.TextField(blank=True, null=True)
gmail_token_expiry = models.DateTimeField(blank=True, null=True)
gmail_profile_updated = models.DateTimeField(blank=True, null=True)
```

### Методы User:
```python
def update_from_gmail(self)      # Обновляет профиль из Gmail
def needs_gmail_refresh(self)    # Проверяет необходимость обновления токена
def refresh_gmail_token(self)    # Обновляет токен доступа
```

## Безопасность

### 1. OAuth 2.0
- Безопасная аутентификация через Google
- Токены доступа с ограниченным сроком действия
- Refresh токены для автоматического обновления

### 2. Области доступа
- `gmail.readonly` - только чтение Gmail
- `userinfo.profile` - информация профиля
- `userinfo.email` - email адрес

### 3. Защита данных
- Токены хранятся в зашифрованном виде
- Нет доступа к содержимому писем
- Пользователь может отключить доступ в любой момент

## Тестирование

### 1. Создание тестового пользователя
```python
from selexia_travel.models import User

user = User.objects.create_user(
    email='tanRan.an@yandex.ru',
    password='testpass123',
    first_name='',
    last_name=''
)
```

### 2. Тестирование подключения
1. Войти под пользователем
2. Перейти в dashboard
3. Нажать "Подключить Gmail"
4. Пройти OAuth авторизацию
5. Проверить обновление профиля

### 3. Тестирование синхронизации
```python
# В Django shell
from selexia_travel.gmail_integration import sync_user_with_gmail

user = User.objects.get(email='tanRan.an@yandex.ru')
success = sync_user_with_gmail(user)
print(f"Синхронизация: {'успешна' if success else 'неудачна'}")
```

## Устранение неполадок

### 1. Ошибка "Invalid Credentials"
- Проверьте правильность GMAIL_CLIENT_ID и GMAIL_CLIENT_SECRET
- Убедитесь, что credentials.json актуален
- Проверьте разрешенные redirect URIs

### 2. Ошибка "Access Denied"
- Проверьте области доступа в Google Cloud Console
- Убедитесь, что Gmail API включен
- Проверьте настройки OAuth consent screen

### 3. Токен не обновляется
- Проверьте наличие refresh_token
- Убедитесь, что токен не истек
- Проверьте логи Django

### 4. Профиль не обновляется
- Проверьте права доступа к Gmail API
- Убедитесь, что пользователь разрешил доступ
- Проверьте логи интеграции

## Мониторинг

### 1. Логи
- Все операции с Gmail API логируются
- Ошибки записываются в Django logs
- Можно настроить отдельный файл логов

### 2. Статистика
- Количество подключенных Gmail аккаунтов
- Частота синхронизации
- Успешность обновлений

### 3. Уведомления
- Email уведомления об ошибках
- Уведомления администратору
- Логирование критических ошибок

## Расширение функциональности

### 1. Дополнительные данные
- Аватар пользователя из Gmail
- Языковые настройки
- Часовой пояс

### 2. Автоматическая синхронизация
- Cron задачи для периодической синхронизации
- Webhook для обновлений профиля
- Интеграция с системой уведомлений

### 3. Аналитика
- Статистика использования Gmail
- Анализ активности пользователей
- Отчеты по интеграции

## Заключение

Gmail интеграция предоставляет пользователям удобный способ автоматического обновления профиля, используя данные из их Gmail аккаунта. Система безопасна, надежна и легко расширяется для дополнительной функциональности.

Для пользователя `tanRan.an@yandex.ru` это означает возможность:
1. Подключить Gmail аккаунт
2. Автоматически получить имя и фамилию
3. Синхронизировать email адрес
4. Управлять подключением через dashboard
