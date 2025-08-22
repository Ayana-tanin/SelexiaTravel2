# 📚 Обзор скриптов для Railway PostgreSQL

Этот документ содержит обзор всех созданных скриптов для настройки PostgreSQL на Railway.

## 🚀 Основные скрипты

### 1. `setup_railway_postgresql.py` - Главный скрипт настройки
**Назначение:** Полная настройка PostgreSQL на Railway
**Функции:**
- ✅ Проверка подключения к базе данных
- ✅ Создание всех таблиц через миграции Django
- ✅ Создание суперпользователя
- ✅ Сбор статических файлов
- ✅ Проверка созданных таблиц

**Запуск:**
```bash
python setup_railway_postgresql.py
```

### 2. `setup_railway_env.py` - Настройка переменных окружения
**Назначение:** Создание файла с переменными окружения для Railway
**Функции:**
- 📝 Запрос DATABASE_URL у пользователя
- 🔧 Создание файла `.env.railway`
- 📋 Инструкции по использованию

**Запуск:**
```bash
python setup_railway_env.py
```

### 3. `test_railway_connection.py` - Тест подключения
**Назначение:** Быстрая проверка подключения к Railway PostgreSQL
**Функции:**
- 🔍 Проверка переменных окружения
- 📡 Тест подключения к базе данных
- 📊 Просмотр существующих таблиц
- 🚨 Диагностика ошибок

**Запуск:**
```bash
python test_railway_connection.py
```

### 4. `check_railway_tables.py` - Проверка таблиц
**Назначение:** Детальная проверка состояния таблиц в базе данных
**Функции:**
- 📊 Подсчет таблиц по типам (Django, приложение, другие)
- 📈 Статистика записей в таблицах
- 🔄 Проверка миграций Django
- 📋 Группировка таблиц

**Запуск:**
```bash
python check_railway_tables.py
```

## 🖥️ Скрипты для разных ОС

### Windows (PowerShell)
**Файл:** `setup_railway.ps1`
**Функции:**
- 🔍 Проверка Python и pip
- 📦 Установка зависимостей
- 🔧 Создание `.env.railway`
- 📡 Тест подключения
- 🗄️ Создание таблиц

**Запуск:**
```powershell
.\setup_railway.ps1
```

### Linux/Mac (Bash)
**Файл:** `setup_railway.sh`
**Функции:**
- 🔍 Проверка Python и pip
- 📦 Установка зависимостей
- 🔧 Создание `.env.railway`
- 📡 Тест подключения
- 🗄️ Создание таблиц

**Запуск:**
```bash
chmod +x setup_railway.sh
./setup_railway.sh
```

## 📖 Документация

### 1. `RAILWAY_POSTGRESQL_SETUP.md` - Полная инструкция
**Содержание:**
- 📋 Предварительные требования
- 🔧 Пошаговая настройка
- 🚨 Устранение неполадок
- 📊 Структура таблиц
- 🔐 Рекомендации по безопасности

### 2. `QUICK_RAILWAY_SETUP.md` - Быстрый старт
**Содержание:**
- ⚡ Настройка за 5 минут
- 🔧 Автоматическая и ручная настройка
- 📋 Что создается автоматически
- 🚨 Быстрое устранение проблем

### 3. `RAILWAY_SCRIPTS_OVERVIEW.md` - Этот файл
**Содержание:**
- 📚 Обзор всех скриптов
- 🚀 Описание функций
- 🖥️ Инструкции по запуску
- 📖 Ссылки на документацию

## 🔄 Последовательность использования

### Вариант 1: Автоматическая настройка (рекомендуется)
```bash
# 1. Настройка переменных окружения
python setup_railway_env.py

# 2. Полная настройка PostgreSQL
python setup_railway_postgresql.py

# 3. Проверка результата
python check_railway_tables.py
```

### Вариант 2: Настройка через ОС-специфичные скрипты
```bash
# Windows
.\setup_railway.ps1

# Linux/Mac
./setup_railway.sh
```

### Вариант 3: Ручная настройка
```bash
# 1. Установите DATABASE_URL
export DATABASE_URL="postgresql://username:password@host:port/database"

# 2. Проверьте подключение
python test_railway_connection.py

# 3. Создайте таблицы
python manage.py migrate

# 4. Создайте суперпользователя
python manage.py createsuperuser
```

## 🚨 Диагностика проблем

### Проверка подключения
```bash
python test_railway_connection.py
```

### Проверка таблиц
```bash
python check_railway_tables.py
```

### Проверка миграций
```bash
python manage.py showmigrations
python manage.py migrate --plan
```

### Проверка Django
```bash
python manage.py check
python manage.py runserver --verbosity=2
```

## 📊 Ожидаемый результат

После успешной настройки у вас должно быть:

### Таблицы Django (системные)
- `auth_user`, `auth_group`, `auth_permission`
- `django_content_type`, `django_migrations`, `django_session`
- `django_site`, `django_admin_log`

### Таблицы приложения
- `selexia_travel_user` - Пользователи
- `selexia_travel_country` - Страны
- `selexia_travel_city` - Города
- `selexia_travel_category` - Категории
- `selexia_travel_excursion` - Экскурсии
- `selexia_travel_booking` - Бронирования
- `selexia_travel_review` - Отзывы
- `selexia_travel_favorite` - Избранное
- `selexia_travel_usersettings` - Настройки пользователей

## 🔐 Безопасность

### Переменные окружения
- ✅ `DATABASE_URL` - подключение к PostgreSQL
- ✅ `SECRET_KEY` - секретный ключ Django
- ✅ `DEBUG=False` - отключение режима отладки
- ✅ `CSRF_COOKIE_SECURE=True` - безопасные куки
- ✅ `SESSION_COOKIE_SECURE=True` - безопасные сессии

### Рекомендации
1. **Измените SECRET_KEY** на уникальное значение
2. **Используйте HTTPS** в продакшене
3. **Ограничьте доступ** к базе данных
4. **Регулярно обновляйте** зависимости

## 📞 Поддержка

### Если что-то пошло не так:
1. **Проверьте логи** Django и Railway
2. **Используйте скрипты диагностики** выше
3. **Обратитесь к документации** Django и Railway
4. **Создайте issue** в репозитории проекта

### Полезные команды:
```bash
# Проверка состояния
python check_railway_tables.py

# Сброс миграций
python manage.py migrate --fake-initial

# Пересоздание таблиц
python manage.py migrate --fake zero
python manage.py migrate
```

---

**Удачи в настройке! 🚀**
