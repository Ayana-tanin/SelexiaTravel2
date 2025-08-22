# Интеграция Vue.js с Django HTML сервером

## Обзор

Этот проект теперь поддерживает два способа работы с Vue.js:

1. **Vue.js SPA** - полноценное одностраничное приложение (как было раньше)
2. **Vue.js HTML шаблоны** - Vue.js компоненты, интегрированные в Django HTML шаблоны

## Что было создано

### 1. Базовый HTML шаблон
- `templates/vue_base.html` - базовый шаблон с подключением всех необходимых библиотек

### 2. Vue.js HTML шаблоны
- `templates/catalog_vue.html` - каталог экскурсий с Vue.js
- `templates/excursion_detail_vue.html` - детальная страница экскурсии с Vue.js

### 3. Django Views
- `catalog_vue()` - view для каталога
- `excursion_detail_vue()` - view для детальной страницы
- API endpoints для работы с данными

### 4. URL маршруты
- `/catalog-vue/` - каталог с Vue.js
- `/excursion-vue/<slug>/` - детальная страница с Vue.js
- `/api-vue/*` - API endpoints для Vue.js

## Запуск проекта

### Шаг 1: Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости (если используете SPA)
npm install
```

### Шаг 2: Запуск Django сервера

```bash
# Активируйте виртуальное окружение (если используете)
# Windows:
selexia_env\Scripts\activate
# Linux/Mac:
source selexia_env/bin/activate

# Запуск сервера
python manage.py runserver
```

### Шаг 3: Открытие в браузере

- **Каталог с Vue.js**: http://127.0.0.1:8000/catalog-vue/
- **Детальная страница**: http://127.0.0.1:8000/excursion-vue/[slug]/
- **Обычный SPA**: http://127.0.0.1:8000/

## Особенности интеграции

### 1. CDN библиотеки
Все необходимые библиотеки подключаются через CDN:
- Vue.js 3
- Vue Router 4
- Pinia (state management)
- Axios (HTTP клиент)
- Tailwind CSS
- Font Awesome

### 2. Передача данных Django → Vue.js
Данные передаются через Django контекст и преобразуются в JavaScript:

```html
<!-- В шаблоне Django -->
<script>
const excursionData = {{ excursion|safe }};
</script>
```

### 3. API endpoints
Vue.js компоненты используют API endpoints для динамической загрузки данных:
- `/api-vue/excursions/` - список экскурсий
- `/api-vue/countries/` - список стран
- `/api-vue/categories/` - список категорий
- `/api-vue/cities/` - список городов

## Структура файлов

```
templates/
├── vue_base.html              # Базовый шаблон с Vue.js
├── catalog_vue.html           # Каталог с Vue.js
├── excursion_detail_vue.html  # Детальная страница с Vue.js
└── vue_spa.html              # Оригинальный SPA шаблон

selexia_travel/
├── views.py                   # Django views для Vue.js
├── urls.py                    # URL маршруты
└── models.py                  # Модели данных
```

## Преимущества нового подхода

### 1. Простота развертывания
- Не нужно собирать Vue.js приложение
- Все работает "из коробки"
- Легко отлаживать

### 2. SEO дружественность
- Страницы рендерятся на сервере
- Поисковые системы видят весь контент
- Быстрая загрузка первой страницы

### 3. Гибкость
- Можно комбинировать Django и Vue.js
- Легко добавлять новые страницы
- Простая интеграция с существующим кодом

## Отладка

### 1. Проверка консоли браузера
Откройте Developer Tools (F12) и проверьте:
- Ошибки JavaScript
- Запросы к API
- Состояние Vue.js приложения

### 2. Проверка Django логов
В терминале с Django сервером будут видны:
- HTTP запросы
- Ошибки Python
- SQL запросы

### 3. Проверка API endpoints
Тестируйте API напрямую:
```bash
curl http://127.0.0.1:8000/api-vue/excursions/
curl http://127.0.0.1:8000/api-vue/countries/
```

## Кастомизация

### 1. Добавление новых страниц
1. Создайте HTML шаблон в `templates/`
2. Добавьте view в `views.py`
3. Добавьте URL в `urls.py`

### 2. Изменение стилей
- Tailwind CSS классы можно изменять прямо в HTML
- Для кастомных стилей используйте `<style>` блоки
- Можно подключить дополнительные CSS файлы

### 3. Добавление функциональности
- Новые Vue.js компоненты
- Дополнительные API endpoints
- Интеграция с Django формами

## Проблемы и решения

### 1. CSRF токены
CSRF токены автоматически передаются в Vue.js через `window.DJANGO_DATA.csrfToken`

### 2. Статические файлы
Убедитесь, что Django правильно обслуживает статические файлы:
```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 3. Медиа файлы
Для изображений экскурсий:
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Производительность

### 1. Кэширование
- Django кэширует шаблоны
- Vue.js кэширует компоненты
- API responses можно кэшировать

### 2. Оптимизация изображений
- Используйте WebP формат
- Lazy loading для изображений
- Responsive images

### 3. Bundle size
- CDN библиотеки кэшируются браузером
- Можно использовать локальные версии для продакшена

## Заключение

Новый подход позволяет:
- Быстро развернуть проект
- Легко отлаживать и поддерживать
- Сохранить все преимущества Vue.js
- Интегрировать с существующим Django кодом

Для продакшена рекомендуется:
- Настроить кэширование
- Оптимизировать изображения
- Использовать CDN для статических файлов
- Настроить мониторинг производительности
