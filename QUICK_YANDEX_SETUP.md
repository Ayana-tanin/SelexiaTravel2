# 🚀 Быстрая настройка Яндекс OAuth

## ⚡ Что нужно сделать за 5 минут

### 1. Создать приложение в Яндекс OAuth
- Перейти на [https://oauth.yandex.ru/](https://oauth.yandex.ru/)
- Нажать "Зарегистрировать новое приложение"
- Заполнить:
  - **Название**: SELEXIA Travel
  - **Платформа**: Веб-сервисы
  - **Callback URL**: `http://localhost:8000/accounts/yandex/login/callback/`
  - **Права**: `login:info`, `login:email`

### 2. Обновить .env файл
```env
YANDEX_CLIENT_ID=ваш-client-id-от-яндекс
YANDEX_CLIENT_SECRET=ваш-client-secret-от-яндекс
```

### 3. Перезапустить сервер
```bash
python manage.py runserver
```

## ✅ Что уже готово

- ✅ Django Allauth настроен
- ✅ Провайдер Яндекс добавлен
- ✅ Кнопки входа добавлены в шаблоны
- ✅ URL-маршруты настроены
- ✅ Модели данных готовы

## 🧪 Проверить работу

1. Открыть `http://localhost:8000/accounts/signup/`
2. Увидеть кнопку "Яндекс"
3. Нажать на кнопку → редирект на Яндекс OAuth

## 🚨 Если не работает

### Ошибка "invalid_scope"
- **Причина**: В настройках Яндекс OAuth указаны неправильные права доступа
- **Решение**: Указать только `login:info` и `login:email` (без `login:avatar`, `login:birthday`)

### Ошибка "MultipleObjectsReturned"
- **Причина**: В базе данных несколько приложений Yandex OAuth
- **Решение**: Удалить дублирующиеся приложения через админ-панель

### Общие проверки
1. Проверить правильность Client ID и Secret в .env
2. Убедиться, что callback URL в Яндекс OAuth правильный: `http://localhost:8000/accounts/yandex/login/callback/`
3. Проверить логи Django
4. Убедиться, что в настройках Django указаны правильные scope: `['login:info', 'login:email']`

---

**Готово!** Пользователи смогут входить через Яндекс аккаунты.
