# Быстрая проверка Dashboard

## Что было изменено

1. **templates/users/dashboard.html** - полностью переписан для работы с реальными данными
2. **selexia_travel/views.py** - обновлен `dashboard_view` для обработки AJAX-запросов и загрузки данных
3. **selexia_travel/models.py** - добавлен импорт `UserSettings`

## Как проверить работу

### 1. Запуск сервера
```bash
python manage.py runserver
```

### 2. Создание тестового пользователя (если нет)
```python
# В Django admin или через shell
from selexia_travel.models import User
user = User.objects.create_user(
    email='test@example.com',
    password='testpass123',
    first_name='Тест',
    last_name='Пользователь'
)
```

### 3. Создание тестовых данных
```python
# В Django shell
from selexia_travel.models import *

# Создание страны и города
country = Country.objects.create(
    name_ru='Кыргызстан',
    name_en='Kyrgyzstan',
    iso_code='KGZ',
    slug='kyrgyzstan'
)

city = City.objects.create(
    name_ru='Бишкек',
    name_en='Bishkek',
    country=country,
    slug='bishkek'
)

# Создание категории
category = Category.objects.create(
    name_ru='Городские экскурсии',
    name_en='City Tours',
    slug='city-tours'
)

# Создание экскурсии
excursion = Excursion.objects.create(
    title_ru='Экскурсия по Бишкеку',
    title_en='Bishkek City Tour',
    description_ru='Увлекательная экскурсия по столице Кыргызстана',
    short_description_ru='Познакомьтесь с историей и культурой Бишкека',
    country=country,
    city=city,
    category=category,
    price=50.00,
    duration=3,
    duration_unit='hours',
    status='published',
    slug='bishkek-city-tour'
)

# Создание бронирования
booking = Booking.objects.create(
    excursion=excursion,
    user=user,
    date='2024-12-20',
    people_count=2,
    total_price=100.00,
    status='confirmed',
    contact_phone='+996555123456',
    contact_email='test@example.com'
)

# Создание отзыва
review = Review.objects.create(
    excursion=excursion,
    user=user,
    rating=5,
    text='Отличная экскурсия! Очень понравилось.'
)
```

### 4. Проверка dashboard
1. Войти в систему под тестовым пользователем
2. Перейти на `/dashboard/`
3. Проверить отображение:
   - Имени пользователя
   - Количества отзывов (1)
   - Потраченной суммы ($100)
   - Отзыва об экскурсии
   - Бронирования

### 5. Тестирование функций
- Переключение между вкладками
- Работа переключателей уведомлений
- Отображение пустых состояний (если данных нет)

## Возможные проблемы

### 1. Пустая страница
- Проверить авторизацию пользователя
- Проверить наличие данных в БД
- Проверить логи Django

### 2. Ошибки 500
- Проверить миграции: `python manage.py migrate`
- Проверить импорты в views.py
- Проверить логи сервера

### 3. Не отображаются изображения
- Проверить настройки MEDIA_URL и MEDIA_ROOT
- Проверить права доступа к папке media

## Результат

После всех изменений dashboard должен:
- Отображать реальные данные пользователя из БД
- Показывать актуальную статистику
- Работать с AJAX-запросами для настроек
- Корректно обрабатывать пустые состояния
- Быть полностью адаптивным для мобильных устройств
