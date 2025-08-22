#!/bin/bash

echo "🚀 Быстрый деплой SelexiaTravel на Railway"
echo "=========================================="

# Проверяем наличие Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите Git и попробуйте снова."
    exit 1
fi

# Проверяем статус Git
if [ ! -d ".git" ]; then
    echo "❌ Это не Git репозиторий. Инициализируйте Git:"
    echo "   git init"
    echo "   git remote add origin <your-repo-url>"
    exit 1
fi

# Проверяем наличие всех необходимых файлов
echo "📋 Проверяем файлы для деплоя..."

required_files=("Procfile" "requirements.txt" "runtime.txt" "build.sh")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Отсутствуют файлы: ${missing_files[*]}"
    echo "   Создайте недостающие файлы и попробуйте снова."
    exit 1
fi

echo "✅ Все файлы на месте!"

# Проверяем статус Git
echo "📊 Проверяем статус Git..."
git_status=$(git status --porcelain)

if [ -n "$git_status" ]; then
    echo "📝 Обнаружены несохраненные изменения:"
    echo "$git_status"
    echo ""
    read -p "Хотите добавить и закоммитить изменения? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "💾 Добавляем изменения..."
        git add .
        read -p "Введите сообщение коммита: " commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Update for Railway deployment"
        fi
        git commit -m "$commit_message"
        echo "✅ Изменения закоммичены!"
    else
        echo "❌ Деплой отменен. Сохраните изменения и попробуйте снова."
        exit 1
    fi
fi

# Проверяем remote origin
if ! git remote get-url origin &> /dev/null; then
    echo "❌ Remote origin не настроен. Настройте его:"
    echo "   git remote add origin <your-repo-url>"
    exit 1
fi

# Показываем текущий remote
echo "🔗 Текущий remote: $(git remote get-url origin)"

# Push в main ветку
echo "🚀 Отправляем изменения в main ветку..."
if git push origin main; then
    echo ""
    echo "🎉 Деплой запущен!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Перейдите на [railway.app](https://railway.app)"
    echo "2. Создайте новый проект"
    echo "3. Выберите 'Deploy from GitHub repo'"
    echo "4. Выберите ваш репозиторий SelexiaTravel"
    echo "5. Настройте переменные окружения (см. RAILWAY_DEPLOYMENT.md)"
    echo "6. Добавьте PostgreSQL базу данных"
    echo ""
    echo "📚 Подробная инструкция: RAILWAY_DEPLOYMENT.md"
else
    echo "❌ Ошибка при отправке в Git. Проверьте права доступа."
    exit 1
fi
