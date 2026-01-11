#!/bin/bash

echo "🚀 Запуск Kaiten Inbox Frontend..."
echo ""

# Проверка зависимостей
if [ ! -d "node_modules" ]; then
    echo "📦 Установка зависимостей..."
    npm install
    echo ""
fi

# Запуск приложения
echo "✅ Frontend запущен на http://localhost:3000"
echo "🔗 Backend должен работать на http://localhost:8000"
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

npm start
