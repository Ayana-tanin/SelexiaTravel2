#!/usr/bin/env python
"""
Простой тест для проверки изображений
"""
import os
import sys
import django

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
django.setup()

from selexia_travel.models import Excursion

def test_images():
    """Тестируем изображения"""
    print("🔍 Тест изображений...")
    
    # Берем первую экскурсию
    excursion = Excursion.objects.first()
    if not excursion:
        print("❌ Нет экскурсий в базе данных")
        return
    
    print(f"🏖️ Тестируем экскурсию: {excursion.title_ru}")
    
    # Проверяем изображения
    images = excursion.images.all()
    print(f"📸 Количество изображений: {images.count()}")
    
    if images.exists():
        first_image = images.first()
        print(f"🖼️ Первое изображение:")
        print(f"   ID: {first_image.id}")
        print(f"   Файл: {first_image.image}")
        print(f"   URL: {first_image.image.url}")
        print(f"   Путь: {first_image.image.path}")
        
        # Проверяем существование файла
        if os.path.exists(first_image.image.path):
            print(f"   ✅ Файл существует")
            print(f"   📏 Размер: {os.path.getsize(first_image.image.path)} байт")
        else:
            print(f"   ❌ Файл НЕ существует")
    else:
        print("❌ Нет изображений у экскурсии")

if __name__ == '__main__':
    test_images()
