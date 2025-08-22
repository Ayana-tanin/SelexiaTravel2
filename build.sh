#!/bin/bash

# Создаем директории для логов если их нет
mkdir -p logs

# Собираем статические файлы
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate

# Создаем суперпользователя если нужно (раскомментировать при необходимости)
# python manage.py createsuperuser --noinput

echo "Build completed successfully!"
