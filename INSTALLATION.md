# 🚀 Установка и настройка SELEXIA Travel

## 📋 Требования

### Python
- Python 3.8+ (рекомендуется 3.11+)
- pip (входит в Python 3.4+)

### Node.js
- Node.js 18+ (рекомендуется LTS версия)
- npm 9+

### База данных
- SQLite (для разработки)
- PostgreSQL (для продакшена)

## 🔧 Быстрая установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd SelexiaTravel
```

### 2. Автоматическая установка зависимостей

#### Python зависимости:
```bash
python install_dependencies.py
```

#### Node.js зависимости:
```bash
node install_node_deps.js
```

## 📦 Ручная установка

### Python зависимости

#### 1. Создание виртуального окружения
```bash
# Windows
python -m venv selexia_env
selexia_env\Scripts\activate

# Linux/Mac
python -m venv selexia_env
source selexia_env/bin/activate
```

#### 2. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Node.js зависимости

#### 1. Установка зависимостей
```bash
npm install
```

## ⚙️ Настройка проекта

### 1. Переменные окружения
Создайте файл `.env` на основе `env_template.txt`:
```bash
cp env_template.txt .env
```

Отредактируйте `.env` файл:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### 2. База данных
```bash
# Активируйте виртуальное окружение
python manage.py makemigrations
python manage.py migrate
```

### 3. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 4. Сборка статических файлов
```bash
# Сборка Vue.js приложения
npm run build

# Сборка Django статических файлов
python manage.py collectstatic
```

## 🚀 Запуск проекта

### 1. Django сервер
```bash
# Активируйте виртуальное окружение
python manage.py runserver
```
Django будет доступен на http://localhost:8000

### 2. Vue.js dev сервер (опционально)
```bash
npm run dev
```
Vue.js будет доступен на http://localhost:3002

## 📁 Структура проекта

```
SelexiaTravel/
├── selexia_travel/          # Django приложение
│   ├── models.py            # Модели данных
│   ├── views.py             # Django views
│   ├── api_views.py         # REST API views
│   └── settings.py          # Настройки Django
├── src/                     # Vue.js приложение
│   ├── components/          # Vue компоненты
│   ├── views/               # Vue страницы
│   ├── stores/              # Pinia stores
│   └── main.js              # Точка входа Vue
├── static/                  # Статические файлы
│   └── dist/                # Собранное Vue.js приложение
├── templates/               # Django шаблоны
└── requirements.txt         # Python зависимости
```

## 🔍 Проверка установки

### 1. Django
- Откройте http://localhost:8000/admin/
- Войдите с созданным суперпользователем
- Проверьте, что все модели доступны

### 2. Vue.js
- Откройте http://localhost:8000/
- Проверьте, что Vue.js приложение загружается
- Проверьте консоль браузера на ошибки

### 3. API
- Откройте http://localhost:8000/api/
- Проверьте, что API endpoints доступны

## 🐛 Решение проблем

### Ошибка "Module not found"
```bash
# Переустановите зависимости
pip install -r requirements.txt
npm install
```

### Ошибка "Database connection failed"
- Проверьте настройки базы данных в `.env`
- Убедитесь, что PostgreSQL запущен (если используется)

### Vue.js не загружается
```bash
# Пересоберите приложение
npm run build
python manage.py collectstatic
```

### Проблемы с Redis
- Убедитесь, что Redis запущен
- Проверьте настройки в `.env`

## 📚 Дополнительные ресурсы

- [Django документация](https://docs.djangoproject.com/)
- [Vue.js документация](https://vuejs.org/guide/)
- [Pinia документация](https://pinia.vuejs.org/)
- [Vite документация](https://vitejs.dev/)

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи Django и браузера
2. Убедитесь, что все зависимости установлены
3. Проверьте версии Python и Node.js
4. Создайте issue в репозитории проекта
