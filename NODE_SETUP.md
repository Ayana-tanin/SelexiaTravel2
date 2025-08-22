# 🚀 Установка Node.js зависимостей и настройка Vue.js

## 📋 Требования

- **Node.js 18+** (рекомендуется LTS версия)
- **npm 9+**

## 🔧 Установка зависимостей

### 1. Проверка версий
```bash
node --version
npm --version
```

### 2. Установка зависимостей
```bash
npm install
```

## 🎯 Что устанавливается

### Основные зависимости:
- **Vue 3.4.0** - прогрессивный JavaScript фреймворк
- **Vite 5.0.0** - быстрый инструмент сборки
- **Vue Router 4.2.5** - маршрутизация для SPA
- **Pinia 2.1.7** - управление состоянием
- **Axios 1.6.2** - HTTP клиент с CSRF поддержкой

### UI библиотеки:
- **Bootstrap 5.3.2** - CSS фреймворк
- **Font Awesome 6.5.1** - иконки
- **Vue I18n 9.8.0** - интернационализация

## ⚙️ Настройка Axios + CSRF

### В `src/main.js`:
```javascript
// Axios с CSRF
import axios from 'axios'

// Настройка Axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

// Получаем CSRF токен из Django контекста
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
if (csrfToken) {
  axios.defaults.headers.common['X-CSRFToken'] = csrfToken
}

// Базовый URL для API
axios.defaults.baseURL = window.DJANGO_CONTEXT?.staticUrl || ''

// Глобальная настройка Axios
window.axios = axios
```

### В HTML шаблонах:
```html
<!-- CSRF Token -->
<meta name="csrf-token" content="{{ csrf_token }}">

<!-- Django контекст -->
<script>
window.DJANGO_CONTEXT = {
    csrfToken: '{{ csrf_token }}',
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken',
    // ... другие настройки
};
</script>
```

## 🏃‍♂️ Запуск

### Разработка:
```bash
npm run dev
```
Vue.js будет доступен на http://localhost:3002

### Продакшен:
```bash
npm run build
```
Собранные файлы будут в `static/dist/`

## 📁 Структура Vue.js приложения

```
src/
├── components/          # Vue компоненты
│   ├── Header.vue      # Шапка сайта
│   ├── Footer.vue      # Подвал
│   ├── ExcursionCard.vue # Карточка экскурсии
│   └── ReviewCard.vue  # Карточка отзыва
├── views/              # Страницы
│   ├── Home.vue        # Главная
│   ├── Catalog.vue     # Каталог
│   ├── ExcursionDetail.vue # Детали экскурсии
│   └── ...            # Другие страницы
├── stores/             # Pinia stores
│   ├── index.js        # Основной store
│   ├── auth.js         # Аутентификация
│   ├── excursion.js    # Экскурсии
│   └── ...            # Другие stores
├── services/           # API сервисы
├── utils/              # Утилиты
├── assets/             # Ресурсы
└── main.js             # Точка входа
```

## 🔒 CSRF защита

### Django настройки:
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]

# CSRF настройки
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Vue.js использование:
```javascript
// В компонентах
this.$axios.post('/api/excursions/', data)
  .then(response => {
    // Успешный запрос
  })
  .catch(error => {
    // Обработка ошибок
  });
```

## 🐛 Решение проблем

### Ошибка "Module not found":
```bash
rm -rf node_modules package-lock.json
npm install
```

### Ошибка CSRF:
- Проверьте наличие `<meta name="csrf-token">` в HTML
- Убедитесь, что Django контекст загружается
- Проверьте настройки CSRF в Django

### Vue.js не загружается:
```bash
npm run build
python manage.py collectstatic
```

## 📚 Дополнительные ресурсы

- [Vue.js документация](https://vuejs.org/guide/)
- [Vite документация](https://vitejs.dev/)
- [Pinia документация](https://pinia.vuejs.org/)
- [Axios документация](https://axios-http.com/)
- [Django CSRF документация](https://docs.djangoproject.com/en/4.2/ref/csrf/)
