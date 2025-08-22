# Компоненты SelexiaTravel

## Обзор

Проект SelexiaTravel теперь использует современные Vue 3 компоненты с Tailwind CSS для стилизации. Основные компоненты были обновлены для соответствия современным стандартам дизайна и UX.

## Основные компоненты

### 1. ExcursionDetail.vue

**Расположение:** `src/components/ExcursionDetail.vue`

**Описание:** Основной компонент для отображения детальной информации об экскурсии. Создан на основе `example.vue` с учетом всех особенностей и правильного отображения данных.

**Особенности:**
- Современный дизайн с использованием Tailwind CSS
- Адаптивная сетка изображений
- Табы для различных разделов (Описание, Программа, Даты, Отзывы, FAQ, Карта)
- Правая панель с формой бронирования
- Sticky навигация
- Мобильная адаптивность

**Использование:**
```vue
<template>
  <ExcursionDetail :excursion="excursionData" />
</template>

<script>
import ExcursionDetail from '@/components/ExcursionDetail.vue'

export default {
  components: {
    ExcursionDetail
  }
}
</script>
```

**Props:**
- `excursion` (Object, required) - объект с данными экскурсии

**Структура данных экскурсии:**
```javascript
{
  id: Number,
  title_ru: String,
  description_ru: String,
  price: Number,
  duration: Number,
  max_group_size: Number,
  average_rating: Number,
  total_reviews: Number,
  city: { name_ru: String },
  country: { name_ru: String },
  category: { name_ru: String },
  images: Array,
  itinerary_ru: String,
  included_services_ru: String,
  excluded_services_ru: String,
  // ... другие поля
}
```

### 2. Catalog.vue (Обновленный)

**Расположение:** `src/views/Catalog.vue`

**Описание:** Обновленный каталог экскурсий с современным дизайном, соответствующим изображению. Включает правую панель фильтров и современный интерфейс.

**Особенности:**
- Современный header с поиском
- Правая панель фильтров (sticky)
- Сетка карточек экскурсий
- Адаптивный дизайн
- Фильтры по стране, категории, цене, длительности, размеру группы
- Поиск по названию и городу

**Фильтры:**
- Город / Страна
- Категория
- Цена (от/до)
- Длительность (от/до)
- Размер группы
- Поиск по тексту

### 3. ExcursionCard.vue

**Расположение:** `src/components/ExcursionCard.vue`

**Описание:** Карточка экскурсии для отображения в каталоге.

**Особенности:**
- Адаптивный дизайн
- Поддержка режимов отображения (grid/list)
- Кнопка избранного
- Рейтинг и отзывы
- Информация о местоположении

## Стилизация

### Tailwind CSS

Проект использует Tailwind CSS для стилизации. Основные классы:

- **Цвета:** `bg-white`, `text-gray-900`, `text-blue-600`
- **Размеры:** `p-4`, `m-6`, `w-80`, `h-48`
- **Скругления:** `rounded-2xl`, `rounded-lg`
- **Тени:** `shadow-sm`, `shadow-lg`
- **Переходы:** `transition-colors`, `transition-shadow`

### Адаптивность

Компоненты адаптированы для различных размеров экранов:

```css
/* Мобильные устройства */
@media (max-width: 768px) { ... }

/* Планшеты */
@media (max-width: 1024px) { ... }

/* Десктоп */
@media (min-width: 1024px) { ... }
```

## Интеграция с существующей системой

### Stores

Компоненты интегрированы с существующими stores:

- `useExcursionStore` - для загрузки данных об экскурсиях
- `useFavoriteStore` - для работы с избранным
- `useAuthStore` - для аутентификации

### API

Компоненты ожидают определенную структуру данных от API:

```javascript
// Пример ответа API для экскурсии
{
  id: 1,
  title_ru: "Название экскурсии",
  description_ru: "Описание экскурсии",
  price: 12000,
  duration: 3,
  max_group_size: 15,
  average_rating: 4.8,
  total_reviews: 25,
  city: { name_ru: "Москва" },
  country: { name_ru: "Россия" },
  category: { name_ru: "Обзорная" },
  images: [
    { image: "/static/images/excursion1.jpg" }
  ]
}
```

## Установка и настройка

### 1. Зависимости

Убедитесь, что установлены необходимые зависимости:

```bash
npm install tailwindcss @tailwindcss/forms
```

### 2. Конфигурация Tailwind

Создайте файл `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### 3. Импорт стилей

В главном CSS файле добавьте:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Использование компонентов

### 1. В каталоге

```vue
<template>
  <div class="catalog-page">
    <Catalog />
  </div>
</template>

<script>
import Catalog from '@/views/Catalog.vue'

export default {
  components: { Catalog }
}
</script>
```

### 2. На странице экскурсии

```vue
<template>
  <div class="excursion-page">
    <ExcursionDetail :excursion="excursion" />
  </div>
</template>

<script>
import ExcursionDetail from '@/components/ExcursionDetail.vue'

export default {
  components: { ExcursionDetail },
  data() {
    return {
      excursion: { /* данные экскурсии */ }
    }
  }
}
</script>
```

## Кастомизация

### Цветовая схема

Для изменения цветовой схемы отредактируйте классы Tailwind в компонентах:

```vue
<!-- Текущий синий цвет -->
<button class="bg-blue-600 text-white">

<!-- Изменить на зеленый -->
<button class="bg-green-600 text-white">
```

### Размеры и отступы

Измените размеры и отступы, используя классы Tailwind:

```vue
<!-- Текущие отступы -->
<div class="p-6">

<!-- Увеличить отступы -->
<div class="p-8">
```

## Поддержка и обновления

### Версионирование

Компоненты версионируются вместе с основным проектом. При обновлении:

1. Проверьте совместимость с новыми версиями Vue
2. Обновите зависимости Tailwind CSS
3. Протестируйте на различных устройствах

### Отладка

Для отладки используйте Vue DevTools и консоль браузера. Основные точки отладки:

- Загрузка данных в `onMounted`
- Обработка ошибок API
- Валидация props
- Состояние фильтров

## Заключение

Новые компоненты обеспечивают современный, адаптивный интерфейс для проекта SelexiaTravel. Они полностью интегрированы с существующей системой и готовы к использованию в продакшене.

Для получения дополнительной информации обратитесь к документации Vue 3 и Tailwind CSS.
