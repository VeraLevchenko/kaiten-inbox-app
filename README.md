# Kaiten Inbox App — Распределение входящих писем

MVP веб-приложение для быстрого "расписывания" входящих писем из Kaiten.

## Структура проекта

```
kaiten-inbox-app/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── samples/          # Примеры файлов для тестирования
├── employees.json    # Список исполнителей
├── .env.example      # Пример конфигурации
└── README.md         # Этот файл
```

## Быстрый старт

### 1. Настройка конфигурации

Скопируйте `.env.example` в `.env` и заполните реальные значения:

```bash
cp .env.example .env
```

### 2. Запуск Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен на http://localhost:8000

### 3. Запуск Frontend

```bash
cd frontend
npm install
npm start
```

Frontend будет доступен на http://localhost:3000

## API Endpoints

- `GET /api/state` — получить текущее состояние очереди
- `POST /api/assign` — назначить исполнителя
- `POST /api/skip` — пропустить письмо
- `POST /api/undo` — отменить последнее действие
- `GET /files/{incoming_no}/{filename}` — получить файл письма

## Структура данных Kaiten

- **Board ID**: 1612419 ("Входящие/Исходящие 2026")
- **Column "Очередь"**: 5592671
- **Column "Назначить исполнителя"**: 5592672
- **Входящий номер**: `card.properties["id_228499"]`

## Логика работы

1. Приложение отображает первое неотписанное письмо (минимальный входящий номер)
2. При назначении исполнителя карточка перемещается в колонку "Назначить исполнителя"
3. Поддерживается:
   - Назначение одного исполнителя
   - Несколько исполнителей (первый = owner, остальные в комментарии)
   - Добавление резолюции (комментария)
   - Отмена последнего действия
   - Пропуск письма (Skip) с логикой партий

## Требования

- Python 3.9+
- Node.js 16+
- Доступ к API Kaiten с токеном
- Папка с файлами писем (FILES_ROOT)
