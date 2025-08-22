#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Установка зависимостей SELEXIA Travel"
echo "================================================"

# Функция для вывода сообщений
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка Python
echo
echo "📋 Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_status "Python3 найден"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_status "Python найден"
else
    print_error "Python не найден! Установите Python 3.8+"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Требуется Python 3.8+, текущая версия: $PYTHON_VERSION"
    exit 1
fi

print_status "Python версия: $PYTHON_VERSION"

# Проверка Node.js
echo
echo "📋 Проверка Node.js..."
if ! command -v node &> /dev/null; then
    print_error "Node.js не найден! Установите Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version)
NODE_MAJOR=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)

if [ "$NODE_MAJOR" -lt 18 ]; then
    print_error "Требуется Node.js 18+, текущая версия: $NODE_VERSION"
    exit 1
fi

print_status "Node.js версия: $NODE_VERSION"

# Проверка npm
if ! command -v npm &> /dev/null; then
    print_error "npm не найден!"
    exit 1
fi

NPM_VERSION=$(npm --version)
print_status "npm версия: $NPM_VERSION"

# Установка Python зависимостей
echo
echo "🔧 Установка Python зависимостей..."
if ! $PYTHON_CMD install_dependencies.py; then
    print_error "Ошибка при установке Python зависимостей"
    exit 1
fi

# Установка Node.js зависимостей
echo
echo "🔧 Установка Node.js зависимостей..."
if ! node install_node_deps.js; then
    print_error "Ошибка при установке Node.js зависимостей"
    exit 1
fi

echo
echo "🎉 Все зависимости установлены успешно!"
echo
echo "📋 Следующие шаги:"
echo "1. Активируйте виртуальное окружение: source selexia_env/bin/activate"
echo "2. Выполните миграции: python manage.py migrate"
echo "3. Создайте суперпользователя: python manage.py createsuperuser"
echo "4. Соберите Vue.js: npm run build"
echo "5. Запустите сервер: python manage.py runserver"
echo
