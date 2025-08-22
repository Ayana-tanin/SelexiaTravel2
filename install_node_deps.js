#!/usr/bin/env node
/**
 * Скрипт для установки Node.js зависимостей SELEXIA Travel
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function runCommand(command, description) {
    console.log(`\n🔧 ${description}...`);
    try {
        execSync(command, { stdio: 'inherit' });
        console.log(`✅ ${description} завершено успешно`);
        return true;
    } catch (error) {
        console.error(`❌ Ошибка при ${description.toLowerCase()}:`, error.message);
        return false;
    }
}

function checkNodeVersion() {
    try {
        const version = execSync('node --version', { encoding: 'utf8' }).trim();
        const majorVersion = parseInt(version.replace('v', '').split('.')[0]);
        
        if (majorVersion < 18) {
            console.error('❌ Требуется Node.js 18+');
            console.error(`Текущая версия: ${version}`);
            process.exit(1);
        }
        
        console.log(`✅ Node.js ${version}`);
        return true;
    } catch (error) {
        console.error('❌ Не удалось определить версию Node.js');
        process.exit(1);
    }
}

function checkNpmVersion() {
    try {
        const version = execSync('npm --version', { encoding: 'utf8' }).trim();
        const majorVersion = parseInt(version.split('.')[0]);
        
        if (majorVersion < 9) {
            console.error('❌ Требуется npm 9+');
            console.error(`Текущая версия: ${version}`);
            process.exit(1);
        }
        
        console.log(`✅ npm ${version}`);
        return true;
    } catch (error) {
        console.error('❌ Не удалось определить версию npm');
        process.exit(1);
    }
}

function main() {
    console.log('🚀 Установка Node.js зависимостей SELEXIA Travel');
    console.log('=' * 50);
    
    // Проверяем версии
    checkNodeVersion();
    checkNpmVersion();
    
    // Проверяем наличие package.json
    if (!fs.existsSync('package.json')) {
        console.error('❌ Файл package.json не найден');
        process.exit(1);
    }
    
    // Устанавливаем зависимости
    if (!runCommand('npm install', 'Установка Node.js зависимостей')) {
        process.exit(1);
    }
    
    // Проверяем наличие src директории
    if (!fs.existsSync('src')) {
        console.error('❌ Директория src не найдена');
        process.exit(1);
    }
    
    console.log('\n🎉 Node.js зависимости установлены успешно!');
    console.log('\n📋 Следующие шаги:');
    console.log('1. Запустите dev сервер: npm run dev');
    console.log('2. Для продакшена: npm run build');
    console.log('3. Vue.js приложение будет доступно на http://localhost:3002');
}

if (require.main === module) {
    main();
}
