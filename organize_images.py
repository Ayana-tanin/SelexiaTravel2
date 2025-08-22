#!/usr/bin/env python
"""
Скрипт для организации изображений по папкам
"""
import os
import shutil
import random

def organize_images():
    """Организует изображения по папкам"""
    
    # Источники изображений
    source_dirs = [
        'media/excursions/covers/',
        'media/excursions/gallery/',
    ]
    
    # Получаем все изображения
    all_images = []
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            for file in os.listdir(source_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    all_images.append(os.path.join(source_dir, file))
    
    if not all_images:
        print("Не найдено изображений для копирования")
        return
    
    # Создаем директории если не существуют
    os.makedirs('static/images/countries', exist_ok=True)
    os.makedirs('static/images/categories', exist_ok=True)
    os.makedirs('static/images/heroes', exist_ok=True)
    
    # Копируем изображения для стран
    print("Копируем изображения для стран...")
    countries = ['turkey.jpg', 'spain.jpg', 'italy.jpg', 'greece.jpg', 'france.jpg']
    for i, country in enumerate(countries):
        if i < len(all_images):
            source = all_images[i]
            dest = f'static/images/countries/{country}'
            try:
                shutil.copy2(source, dest)
                print(f"  {country} <- {source}")
            except Exception as e:
                print(f"  Ошибка копирования {source}: {e}")
    
    # Копируем изображения для категорий
    print("Копируем изображения для категорий...")
    categories = ['nature.jpg', 'mountains.jpg', 'city.jpg', 'transfer.jpg']
    for i, category in enumerate(categories):
        if i + 5 < len(all_images):
            source = all_images[i + 5]
            dest = f'static/images/categories/{category}'
            try:
                shutil.copy2(source, dest)
                print(f"  {category} <- {source}")
            except Exception as e:
                print(f"  Ошибка копирования {source}: {e}")
    
    # Копируем изображения для героев страниц
    print("Копируем изображения для героев страниц...")
    heroes = ['home-hero.jpg', 'catalog-hero.jpg', 'about-hero.jpg']
    for i, hero in enumerate(heroes):
        if i + 9 < len(all_images):
            source = all_images[i + 9]
            dest = f'static/images/heroes/{hero}'
            try:
                shutil.copy2(source, dest)
                print(f"  {hero} <- {source}")
            except Exception as e:
                print(f"  Ошибка копирования {source}: {e}")
    
    print("Организация изображений завершена!")

if __name__ == '__main__':
    organize_images()
