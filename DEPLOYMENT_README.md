# 🚀 Руководство по развертыванию SelexiaTravel

Этот документ содержит пошаговые инструкции по развертыванию проекта SelexiaTravel в продакшене с PostgreSQL.

## 📋 Предварительные требования

### 🔧 Системные требования:
- **OS:** Windows 10+, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python:** 3.8+
- **RAM:** Минимум 2GB, рекомендуется 4GB+
- **Диск:** Минимум 5GB свободного места
- **PostgreSQL:** 12+

### 📦 Программное обеспечение:
- **PostgreSQL** - база данных
- **Redis** (опционально) - кэширование и Celery
- **Nginx** (опционально) - веб-сервер
- **Gunicorn** (опционально) - WSGI сервер

## 🗄️ Установка PostgreSQL

### Windows:
1. Скачайте установщик с [официального сайта](https://www.postgresql.org/download/windows/)
2. Запустите установщик и следуйте инструкциям
3. Запомните пароль для пользователя `postgres`
4. Добавьте PostgreSQL в PATH

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS:
```bash
brew install postgresql
brew services start postgresql
```

## 🚀 Быстрое развертывание

### 1. Клонирование и настройка:
```bash
# Клонируйте проект
git clone <your-repo-url>
cd SelexiaTravel

# Активируйте виртуальное окружение
selexia_env\Scripts\activate  # Windows
source selexia_env/bin/activate  # Linux/macOS

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка PostgreSQL:
```bash
# Запустите скрипт настройки
python setup_postgresql.py
```

### 3. Создание суперпользователя:
```bash
# Создайте админа
python create_admin.py
```

### 4. Запуск проекта:
```bash
# Выполните миграции
python manage.py migrate

# Соберите статические файлы
python manage.py collectstatic

# Запустите сервер
python manage.py runserver
```

## 🔧 Детальная настройка

### Настройка базы данных PostgreSQL:

1. **Подключитесь к PostgreSQL:**
```bash
psql -U postgres -h localhost
```

2. **Создайте пользователя и базу данных:**
```sql
CREATE USER selexia_user WITH PASSWORD 'selexia_password';
CREATE DATABASE selexia_travel_db OWNER selexia_user;
GRANT ALL PRIVILEGES ON DATABASE selexia_travel_db TO selexia_user;
\q
```

3. **Проверьте подключение:**
```bash
psql -U selexia_user -h localhost -d selexia_travel_db -c "SELECT version();"
```

### Настройка переменных окружения:

Создайте файл `.env` в корне проекта:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database - PostgreSQL
DATABASE_URL=postgresql://selexia_user:selexia_password@localhost:5432/selexia_travel_db

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Security Settings
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

## 🌐 Настройка веб-сервера

### Nginx + Gunicorn (рекомендуется):

1. **Установите Gunicorn:**
```bash
pip install gunicorn
```

2. **Создайте systemd сервис:**
```bash
sudo nano /etc/systemd/system/selexiatravel.service
```

```ini
[Unit]
Description=SelexiaTravel Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/SelexiaTravel
ExecStart=/path/to/SelexiaTravel/selexia_env/bin/gunicorn --workers 3 --bind unix:/path/to/SelexiaTravel/selexiatravel.sock selexia_travel.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Настройте Nginx:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/SelexiaTravel;
    }

    location /media/ {
        root /path/to/SelexiaTravel;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/SelexiaTravel/selexiatravel.sock;
    }
}
```

## 🔒 Настройка безопасности

### SSL/HTTPS:
1. **Получите SSL сертификат** (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

2. **Обновите .env файл:**
```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Firewall:
```bash
# Ubuntu/Debian
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 Мониторинг и логирование

### Логи Django:
```bash
# Просмотр логов
tail -f logs/django.log

# Ротация логов (logrotate)
sudo nano /etc/logrotate.d/selexiatravel
```

### Мониторинг базы данных:
```bash
# Статистика PostgreSQL
psql -U selexia_user -d selexia_travel_db -c "SELECT * FROM pg_stat_database;"

# Размер базы данных
psql -U selexia_user -d selexia_travel_db -c "SELECT pg_size_pretty(pg_database_size('selexia_travel_db'));"
```

## 🚨 Устранение неполадок

### Частые проблемы:

1. **Ошибка подключения к PostgreSQL:**
```bash
# Проверьте статус сервиса
sudo systemctl status postgresql

# Проверьте логи
sudo tail -f /var/log/postgresql/postgresql-*.log
```

2. **Ошибка миграций:**
```bash
# Сбросьте миграции
python manage.py migrate --fake-initial

# Проверьте статус
python manage.py showmigrations
```

3. **Проблемы с правами доступа:**
```bash
# Проверьте права пользователя
sudo -u postgres psql -c "\du"

# Предоставьте права
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE selexia_travel_db TO selexia_user;"
```

## 📈 Оптимизация производительности

### База данных:
```sql
-- Создайте индексы для часто используемых полей
CREATE INDEX idx_excursion_title ON selexia_travel_excursion(title_ru);
CREATE INDEX idx_booking_date ON selexia_travel_booking(created_at);

-- Анализируйте производительность
ANALYZE selexia_travel_excursion;
```

### Django настройки:
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Оптимизация запросов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'selexia_travel_db',
        'USER': 'selexia_user',
        'PASSWORD': 'selexia_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}
```

## 🔄 Обновление проекта

### Автоматическое обновление:
```bash
#!/bin/bash
# update.sh
cd /path/to/SelexiaTravel
git pull origin main
source selexia_env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart selexiatravel
sudo systemctl reload nginx
```

## 📞 Поддержка

### Полезные команды:
```bash
# Статус сервисов
sudo systemctl status postgresql nginx selexiatravel

# Проверка логов
sudo journalctl -u selexiatravel -f

# Мониторинг ресурсов
htop
iotop
```

### Контакты:
- **Документация:** README.md
- **Issues:** GitHub Issues
- **Поддержка:** Создайте issue в репозитории

---

**🎉 Удачного развертывания!**
