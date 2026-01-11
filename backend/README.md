# Backend API Documentation

## Запуск сервера

```bash
cd backend
./run.sh
```

Или напрямую:
```bash
cd backend
python main.py
```

Сервер запустится на `http://localhost:8000`

## Endpoints

### GET / 
Информация о API

**Response:**
```json
{
  "app": "Kaiten Inbox API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": { ... }
}
```

### GET /api/state
Получить текущее состояние очереди

**Response:**
```json
{
  "queue_count": 5,
  "deferred_count": 0,
  "assigned_session_count": 0,
  "current_card": {
    "card_id": 12345,
    "title": "Запрос на согласование договора",
    "incoming_no": 1233,
    "files": [
      {
        "name": "sample_letter.txt",
        "url": "/files/1233/sample_letter.txt",
        "ext": "txt"
      }
    ]
  }
}
```

### POST /api/assign
Назначить исполнителя

**Request:**
```json
{
  "card_id": 12345,
  "owner_id": 100001,
  "co_owner_ids": [],
  "comment_text": "Резолюция руководителя",
  "multi": false
}
```

**Response:** AppState (см. /api/state)

### POST /api/skip
Пропустить письмо

**Request:**
```json
{
  "card_id": 12345
}
```

**Response:** AppState

### POST /api/undo
Отменить последнее действие

**Request:** пустой body

**Response:** AppState

### GET /files/{incoming_no}/{filename}
Получить файл письма

**Example:** `GET /files/1233/sample_letter.txt`

**Response:** Файл (FileResponse)

## Текущий статус (ЭТАП 1)

✅ Сервер запускается  
✅ Все endpoints работают с моковыми данными  
✅ Отдача файлов работает  
✅ CORS настроен для frontend  

🔄 В следующих этапах:
- Подключение к реальному API Kaiten
- Логика обработки очереди
- Сохранение состояния
