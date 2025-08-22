# 🚀 Быстрый старт SELEXIA Travel

## ⚡ 5 минут до запуска

### 1. Python зависимости
```bash
# Активируйте виртуальное окружение
selexia_env\Scripts\activate  # Windows
# source selexia_env/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt
```

### 2. Node.js зависимости
```bash
npm install
```

### 3. База данных
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Сборка Vue.js
```bash
npm run build
```

### 5. Запуск
```bash
python manage.py runserver
```

## 🌐 Доступ к сайту

- **Django**: http://localhost:8000
- **Vue.js dev**: http://localhost:3002 (опционально)
- **Admin**: http://localhost:8000/admin

## 🔧 Что уже настроено

✅ **Django 4.2.10** с Django Allauth  
✅ **Vue 3 + Vite** с Pinia  
✅ **Axios + CSRF** защита  
✅ **Bootstrap 5** + Font Awesome  
✅ **Мультиязычность** (ru/en)  
✅ **REST API** готов к использованию  

## 📁 Основные файлы

- `src/main.js` - Vue.js точка входа + Axios настройки
- `templates/*.html` - Django шаблоны с CSRF токенами
- `src/stores/` - Pinia stores для управления состоянием
- `vite.config.js` - конфигурация сборки

## 🚨 Если что-то не работает

1. **Проверьте версии**: Python 3.8+, Node.js 18+
2. **Переустановите зависимости**: `pip install -r requirements.txt` и `npm install`
3. **Очистите кэш**: `npm run build` и `python manage.py collectstatic`

## 📚 Подробная документация

- [INSTALLATION.md](INSTALLATION.md) - полная установка
- [NODE_SETUP.md](NODE_SETUP.md) - настройка Vue.js
- [README.md](README.md) - описание проекта

---

**SELEXIA Travel** готов к разработке! 🎯
