# 🎯 Django-шаблоны + точки монтирования Vue.js

## 📋 Обзор

Создана структура Django-шаблонов с точками монтирования для Vue.js компонентов. Каждая страница имеет свой контейнер для монтирования Vue.js приложения.

## 🏗️ Структура файлов

### Компоненты навигации и футера
- `templates/components/navigation.html` - Навигационная панель
- `templates/components/footer.html` - Футер сайта

### Основные шаблоны
- `templates/base.html` - Базовый шаблон с навигацией/футером и подключением бандлов
- `templates/catalog.html` - Каталог экскурсий с точкой монтирования `#catalog-app`
- `templates/excursion_detail.html` - Детальная страница экскурсии с точками монтирования
- `templates/profile.html` - Личный кабинет с точкой монтирования `#profile-app`

## 🔧 Настройка

### 1. Подключение Vite бандлов

В `base.html` настроено подключение бандлов:

```html
<!-- Режим разработки -->
{% if DEBUG %}
    <script type="module" src="http://localhost:3002/@vite/client"></script>
    <script type="module" src="http://localhost:3002/src/main.js"></script>
{% else %}
    <!-- Продакшен -->
    <link href="{% static 'dist/assets/main.css' %}" rel="stylesheet">
    <script src="{% static 'dist/assets/main.js' %}" defer></script>
{% endif %}
```

### 2. Точки монтирования

#### Каталог (`catalog.html`)
```html
<div id="catalog-app">
    <!-- Vue.js приложение каталога -->
</div>
```

#### Детальная страница (`excursion_detail.html`)
```html
<div id="reviews-app">
    <!-- Vue.js приложение отзывов -->
</div>
<div id="similar-excursions-app">
    <!-- Vue.js приложение похожих экскурсий -->
</div>
<div id="booking-app">
    <!-- Vue.js приложение бронирования -->
</div>
```

#### Профиль (`profile.html`)
```html
<div id="profile-app">
    <!-- Vue.js приложение профиля -->
</div>
```

### 3. Контекст Django

Каждая страница получает контекст через `window.DJANGO_CONTEXT`:

```html
{% block page_data %}
{
    "pageType": "catalog",
    "filters": {...},
    "sorting": "popularity",
    "viewMode": "grid"
}
{% endblock %}
```

### 4. Инициализация Vue.js

Каждая страница имеет скрипт инициализации:

```html
{% block mount_script %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (window.Vue && window.CatalogApp) {
        const app = window.Vue.createApp(window.CatalogApp);
        app.mount('#catalog-app');
    }
});
</script>
{% endblock %}
```

## 🎨 Особенности дизайна

### Адаптивная навигация
- Мобильное меню с гамбургером
- Выпадающие меню для пользователя и языков
- Поиск с автодополнением

### Фильтры каталога
- Боковая панель с фильтрами
- Поиск по названию
- Фильтры по категориям, цене, длительности, рейтингу
- Сортировка и переключение вида

### Детальная страница экскурсии
- Hero секция с основной информацией
- Галерея изображений с миниатюрами
- Информация об экскурсии
- Форма бронирования
- Отзывы и похожие экскурсии

### Личный кабинет
- Боковая панель с навигацией
- Статистика пользователя
- Вкладки для разных разделов
- Формы редактирования профиля

## 🚀 Следующие шаги

### 1. Создание Vue.js компонентов
Необходимо создать Vue.js приложения для каждой точки монтирования:

- `CatalogApp` - для каталога
- `ReviewsApp` - для отзывов
- `SimilarExcursionsApp` - для похожих экскурсий
- `BookingApp` - для бронирования
- `ProfileApp` - для профиля

### 2. Настройка Vite
Убедиться, что Vite настроен для вывода в `static/dist`:

```javascript
// vite.config.js
export default {
  build: {
    outDir: 'static/dist',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
}
```

### 3. Сборка и деплой
```bash
# Разработка
npm run dev

# Сборка для продакшена
npm run build

# Сборка Django статических файлов
python manage.py collectstatic
```

## 🔒 Безопасность

- CSRF токены добавлены во все формы
- Axios настроен для автоматической отправки CSRF токенов
- Проверка аутентификации пользователя

## 📱 Адаптивность

- Bootstrap 5 для responsive дизайна
- Мобильная навигация
- Адаптивные сетки для экскурсий
- Touch-friendly элементы управления

## 🌐 Интернационализация

- Поддержка русского и английского языков
- Использование Django i18n
- Переключатель языков в навигации

## 📊 Производительность

- Lazy loading для изображений
- Оптимизированные запросы к API
- Кэширование статических файлов
- Минификация CSS и JavaScript в продакшене

---

**Готово к интеграции с Vue.js компонентами!** 🎉
