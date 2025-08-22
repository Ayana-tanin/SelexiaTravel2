#!/usr/bin/env python
"""
Скрипт для создания тестовых данных для dashboard
"""
import os
import sys
import django
from datetime import date, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
django.setup()

from django.contrib.auth import get_user_model
from selexia_travel.models import (
    User, Country, City, Category, Excursion, 
    ExcursionImage, Review, Booking, Favorite, UserSettings
)

User = get_user_model()

def create_test_data():
    """Создает тестовые данные для dashboard"""
    print("Создание тестовых данных для dashboard...")
    
    # Создаем тестового пользователя
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '+79001234567',
            'is_active': True
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Создан пользователь: {user.email}")
    else:
        print(f"Пользователь уже существует: {user.email}")
    
    # Создаем настройки пользователя
    settings, created = UserSettings.objects.get_or_create(user=user)
    if created:
        print("Созданы настройки пользователя")
    
    # Создаем страну
    country, created = Country.objects.get_or_create(
        name_ru='Италия',
        defaults={
            'name_en': 'Italy',
            'iso_code': 'ITA',
            'slug': 'italy'
        }
    )
    if created:
        print(f"Создана страна: {country.name_ru}")
    
    # Создаем город
    city, created = City.objects.get_or_create(
        name_ru='Рим',
        country=country,
        defaults={
            'name_en': 'Rome',
            'slug': 'rome'
        }
    )
    if created:
        print(f"Создан город: {city.name_ru}")
    
    # Создаем категорию
    category, created = Category.objects.get_or_create(
        name_ru='Исторические экскурсии',
        defaults={
            'name_en': 'Historical Tours',
            'slug': 'historical-tours',
            'description_ru': 'Экскурсии по историческим местам',
            'description_en': 'Tours to historical places'
        }
    )
    if created:
        print(f"Создана категория: {category.name_ru}")
    
    # Создаем экскурсию
    excursion, created = Excursion.objects.get_or_create(
        title_ru='Экскурсия по Колизею',
        defaults={
            'title_en': 'Colosseum Tour',
            'description_ru': 'Увлекательная экскурсия по древнему амфитеатру',
            'description_en': 'Exciting tour of the ancient amphitheater',
            'short_description_ru': 'Погружение в историю Древнего Рима',
            'short_description_en': 'Immersion in the history of Ancient Rome',
            'country': country,
            'city': city,
            'category': category,
            'price': 50.00,
            'currency': 'EUR',
            'duration': 3,
            'duration_unit': 'hours',
            'max_people': 15,
            'status': 'published',
            'slug': 'colosseum-tour',
            'rating': 4.8,
            'reviews_count': 12,
            'is_popular': True
        }
    )
    if created:
        print(f"Создана экскурсия: {excursion.title_ru}")
    
    # Создаем бронирование
    booking, created = Booking.objects.get_or_create(
        user=user,
        excursion=excursion,
        date=date.today() + timedelta(days=7),
        defaults={
            'people_count': 2,
            'total_price': 100.00,
            'status': 'confirmed',
            'contact_phone': '+79001234567',
            'contact_email': 'test@example.com'
        }
    )
    if created:
        print(f"Создано бронирование на {booking.date}")
    
    # Создаем отзыв
    review, created = Review.objects.get_or_create(
        user=user,
        excursion=excursion,
        defaults={
            'rating': 5,
            'text': 'Отличная экскурсия! Гид был очень знающим и дружелюбным. Рекомендую всем!'
        }
    )
    if created:
        print(f"Создан отзыв с рейтингом {review.rating}")
    
    # Создаем избранное
    favorite, created = Favorite.objects.get_or_create(
        user=user,
        excursion=excursion,
        defaults={
            'item_type': 'excursion'
        }
    )
    if created:
        print(f"Экскурсия добавлена в избранное")
    
    # Создаем еще одну экскурсию для разнообразия
    excursion2, created = Excursion.objects.get_or_create(
        title_ru='Прогулка по Ватикану',
        defaults={
            'title_en': 'Vatican Walk',
            'description_ru': 'Знакомство с сокровищами Ватикана',
            'description_en': 'Introduction to the treasures of the Vatican',
            'short_description_ru': 'Ватиканские музеи и Сикстинская капелла',
            'short_description_en': 'Vatican Museums and Sistine Chapel',
            'country': country,
            'city': city,
            'category': category,
            'price': 75.00,
            'currency': 'EUR',
            'duration': 4,
            'duration_unit': 'hours',
            'max_people': 20,
            'status': 'published',
            'slug': 'vatican-walk',
            'rating': 4.9,
            'reviews_count': 8,
            'is_popular': True
        }
    )
    if created:
        print(f"Создана экскурсия: {excursion2.title_ru}")
    
    # Создаем второе бронирование
    booking2, created = Booking.objects.get_or_create(
        user=user,
        excursion=excursion2,
        date=date.today() + timedelta(days=14),
        defaults={
            'people_count': 1,
            'total_price': 75.00,
            'status': 'pending',
            'contact_phone': '+79001234567',
            'contact_email': 'test@example.com'
        }
    )
    if created:
        print(f"Создано бронирование на {booking2.date}")
    
    print("\nТестовые данные созданы успешно!")
    print(f"Пользователь: {user.email}")
    print(f"Пароль: testpass123")
    print(f"Создано экскурсий: {Excursion.objects.count()}")
    print(f"Создано бронирований: {Booking.objects.count()}")
    print(f"Создано отзывов: {Review.objects.count()}")
    print(f"Создано избранного: {Favorite.objects.count()}")

if __name__ == '__main__':
    create_test_data()
