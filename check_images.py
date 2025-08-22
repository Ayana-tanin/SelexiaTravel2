#!/usr/bin/env python
"""
Скрипт для проверки изображений в базе данных Django
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selexia_travel.settings')
django.setup()

from selexia_travel.models import Excursion, ExcursionImage

def check_images():
    """Проверяем изображения в базе данных"""
    print("🔍 Проверка изображений в базе данных...")
    print("=" * 50)
    
    # Проверяем экскурсии
    excursions = Excursion.objects.all()
    print(f"📊 Всего экскурсий: {excursions.count()}")
    
    for excursion in excursions:
        print(f"\n🏖️ Экскурсия: {excursion.title_ru}")
        print(f"   Slug: {excursion.slug}")
        print(f"   Статус: {excursion.status}")
        
        # Проверяем изображения
        images = excursion.images.all()
        print(f"   📸 Изображений: {images.count()}")
        
        if images.exists():
            for i, img in enumerate(images):
                print(f"      {i+1}. ID: {img.id}")
                print(f"         Файл: {img.image}")
                print(f"         URL: {img.image.url if img.image else 'НЕТ ФАЙЛА'}")
                print(f"         Подпись: {img.caption_ru}")
                print(f"         Порядок: {img.order}")
                
                # Проверяем существование файла
                if img.image:
                    file_path = img.image.path
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"         ✅ Файл существует, размер: {file_size} байт")
                    else:
                        print(f"         ❌ Файл НЕ существует: {file_path}")
                else:
                    print(f"         ❌ Поле image пустое")
        else:
            print("      ❌ Нет изображений")
    
    print("\n" + "=" * 50)
    print("🏁 Проверка завершена!")

if __name__ == '__main__':
    check_images()
