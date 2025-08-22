# 🚂 Развертывание SelexiaTravel на Railway

Это руководство поможет развернуть проект SelexiaTravel на платформе Railway.

## 📋 Предварительные требования

- ✅ GitHub репозиторий с проектом
- ✅ Аккаунт на [Railway.app](https://railway.app/)
- ✅ Готовый Django проект

## 🔧 1. Подготовка проекта

### **Созданные файлы:**
- ✅ `Procfile` - указывает Railway как запускать проект
- ✅ `requirements.txt` - обновлен с gunicorn
- ✅ `railway_settings.py` - настройки для Railway
- ✅ `railway_deploy.py` - скрипт автоматического развертывания
- ✅ `selexia_travel/settings.py` - обновлен для Railway

### **Проверьте наличие файлов:**
```bash
ls -la
# Должны быть:
# - Procfile
# - requirements.txt
# - railway_settings.py
# - railway_deploy.py
# - selexia_travel/settings.py
```

## 🚂 2. Настройка Railway

### **Шаг 1: Создание проекта**
1. Зайдите на [Railway.app](https://railway.app/)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий `SelexiaTravel`

### **Шаг 2: Добавление PostgreSQL**
1. В проекте Railway нажмите "Add"
2. Выберите "Database" → "PostgreSQL"
3. Railway автоматически создаст базу данных

### **Шаг 3: Настройка переменных окружения**
В разделе "Variables" добавьте:

```env
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
RAILWAY_ENVIRONMENT=True

# Database - Railway PostgreSQL
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_HOST=containers-us-west-XX.railway.app
POSTGRES_PORT=XXXXX

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selexiatravelauth@gmail.com
EMAIL_HOST_PASSWORD=afjs pirk rdtg tqyw
DEFAULT_FROM_EMAIL=selexiatravelauth@gmail.com

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

**⚠️ Важно:** Значения `POSTGRES_*` Railway предоставит автоматически после добавления PostgreSQL.

## 🗄️ 3. Настройка базы данных

### **Автоматическая настройка:**
После добавления PostgreSQL Railway автоматически:
- ✅ Создаст базу данных
- ✅ Предоставит переменные окружения
- ✅ Настроит подключение

### **Проверка подключения:**
В Railway Shell выполните:
```bash
python railway_deploy.py
```

Этот скрипт:
- ✅ Проверит Railway окружение
- ✅ Подключится к базе данных
- ✅ Выполнит миграции
- ✅ Соберет статические файлы
- ✅ Создаст суперпользователя

## 📦 4. Развертывание

### **Автоматическое развертывание:**
1. Railway автоматически прочитает `requirements.txt`
2. Установит все зависимости
3. Запустит проект согласно `Procfile`

### **Ручное выполнение команд:**
Если нужно выполнить команды вручную:

```bash
# В Railway Shell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 🌍 5. Домен и доступ

### **Railway домен:**
- Railway предоставит URL вида: `https://your-app.up.railway.app`
- Этот домен автоматически добавлен в `ALLOWED_HOSTS`

### **Доступные URL:**
- 🌐 **Сайт:** `https://your-app.up.railway.app`
- 👤 **Админ-панель:** `https://your-app.up.railway.app/admin/`
- 🔑 **Логин:** `admin`
- 🔐 **Пароль:** `admin123`

## 🔍 6. Мониторинг и логи

### **Просмотр логов:**
1. В Railway проекте перейдите в "Deployments"
2. Выберите последний деплой
3. Нажмите "View Logs"

### **Проверка статуса:**
- ✅ **Deployments** - статус развертывания
- ✅ **Variables** - переменные окружения
- ✅ **Database** - статус PostgreSQL
- ✅ **Settings** - настройки проекта

## 🚨 7. Устранение неполадок

### **Ошибка: "No module named 'gunicorn'"**
```bash
# Решение: проверьте requirements.txt
# Должна быть строка: gunicorn==21.2.0
```

### **Ошибка: "Database connection failed"**
```bash
# Решение: проверьте переменные POSTGRES_*
# Убедитесь что PostgreSQL добавлен в проект
```

### **Ошибка: "Static files not found"**
```bash
# Решение: выполните в Railway Shell
python manage.py collectstatic --noinput
```

### **Ошибка: "Migrations not applied"**
```bash
# Решение: выполните в Railway Shell
python manage.py migrate
```

## 🔄 8. Обновление проекта

### **Автоматическое обновление:**
1. Запушьте изменения в GitHub
2. Railway автоматически пересоберет проект
3. Примените миграции в Railway Shell:
```bash
python railway_deploy.py
```

### **Ручное обновление:**
```bash
# В Railway Shell
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
```

## 📊 9. Проверка работоспособности

### **Тест основных функций:**
1. ✅ Открытие главной страницы
2. ✅ Работа каруселей (Все страны, Популярные экскурсии, Отзывы)
3. ✅ Вход в админ-панель
4. ✅ Проверка базы данных

### **Проверка производительности:**
- ⚡ Время загрузки страниц
- 🗄️ Скорость запросов к БД
- 📱 Адаптивность на мобильных устройствах

## 🎯 10. Финальная проверка

### **Чек-лист развертывания:**
- [ ] Проект создан на Railway
- [ ] PostgreSQL добавлен
- [ ] Переменные окружения настроены
- [ ] Проект успешно развернут
- [ ] Миграции применены
- [ ] Статические файлы собраны
- [ ] Суперпользователь создан
- [ ] Сайт доступен по Railway домену
- [ ] Админ-панель работает
- [ ] Все функции сайта работают

## 🎉 Заключение

**Ваш проект SelexiaTravel успешно развернут на Railway!**

### **Преимущества Railway:**
- 🚀 Быстрое развертывание
- 🗄️ Автоматическая настройка PostgreSQL
- 🔒 SSL сертификаты включены
- 📊 Мониторинг и логи
- 🔄 Автоматические обновления

### **Следующие шаги:**
1. Настройте кастомный домен (опционально)
2. Добавьте мониторинг производительности
3. Настройте резервное копирование БД
4. Оптимизируйте настройки для продакшена

---

**🚂 Удачного развертывания на Railway!**
