# Деплой SelexiaTravel на Railway

## Подготовка проекта

### 1. Убедитесь, что у вас есть все необходимые файлы:
- ✅ `Procfile` - для запуска приложения
- ✅ `requirements.txt` - с зависимостями
- ✅ `runtime.txt` - версия Python
- ✅ `build.sh` - скрипт сборки
- ✅ `.dockerignore` - оптимизация

### 2. Настройте Git репозиторий:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Деплой на Railway

### Шаг 1: Создание аккаунта
1. Перейдите на [railway.app](https://railway.app)
2. Войдите через GitHub
3. Создайте новый проект

### Шаг 2: Подключение репозитория
1. Выберите "Deploy from GitHub repo"
2. Выберите ваш репозиторий `SelexiaTravel`
3. Нажмите "Deploy Now"

### Шаг 3: Настройка переменных окружения
В разделе "Variables" добавьте следующие переменные:

#### Обязательные:
```
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
```

#### База данных:
- Railway автоматически создаст `DATABASE_URL`
- Убедитесь, что он добавлен в переменные

#### Email (если нужен):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@selexiatravel.com
```

#### OAuth (если нужен):
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
YANDEX_CLIENT_ID=your-yandex-client-id
YANDEX_CLIENT_SECRET=your-yandex-client-secret
```

#### Безопасность:
```
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app
```

### Шаг 4: Настройка базы данных
1. В разделе "New" выберите "Database" → "PostgreSQL"
2. Railway автоматически создаст `DATABASE_URL`
3. Скопируйте его в переменные окружения

### Шаг 5: Настройка домена
1. В разделе "Settings" → "Domains"
2. Railway предоставит URL вида: `https://your-app-name.railway.app`
3. Добавьте этот домен в `CSRF_TRUSTED_ORIGINS`

## Автоматический деплой

### При каждом push в main ветку:
1. Railway автоматически пересоберет проект
2. Применит миграции
3. Перезапустит приложение

### Ручной деплой:
1. В разделе "Deployments"
2. Нажмите "Deploy" → "Deploy latest commit"

## Мониторинг и логи

### Просмотр логов:
1. В разделе "Deployments"
2. Выберите последний деплой
3. Нажмите "View Logs"

### Мониторинг:
- Railway автоматически отслеживает здоровье приложения
- При ошибках отправляет уведомления

## Решение проблем

### Ошибка "Build failed":
1. Проверьте `requirements.txt`
2. Убедитесь, что все зависимости совместимы
3. Проверьте логи сборки

### Ошибка "Application Error":
1. Проверьте переменные окружения
2. Убедитесь, что `DATABASE_URL` корректный
3. Проверьте логи приложения

### Проблемы с базой данных:
1. Убедитесь, что PostgreSQL запущен
2. Проверьте миграции: `python manage.py showmigrations`
3. При необходимости: `python manage.py migrate --run-syncdb`

## Оптимизация

### Статические файлы:
- Railway автоматически раздает статические файлы
- Убедитесь, что `STATIC_ROOT` настроен правильно

### Медиа файлы:
- Для продакшена рекомендуется использовать AWS S3 или Cloudinary
- Обновите `MEDIA_URL` и `MEDIA_ROOT` соответственно

### Кэширование:
- Railway поддерживает Redis
- Добавьте Redis add-on для улучшения производительности

## Обновление приложения

### Автоматическое:
- Просто сделайте push в main ветку
- Railway автоматически обновит приложение

### Ручное:
1. В Railway Dashboard
2. Выберите "Deploy" → "Deploy latest commit"

## Поддержка

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [GitHub Issues](https://github.com/railwayapp/railway/issues)
