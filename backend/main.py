"""
Kaiten Inbox App - Backend
FastAPI приложение для распределения входящих писем
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path
import json

# Инициализация FastAPI
app = FastAPI(title="Kaiten Inbox API", version="1.0.0")

# CORS для работы с React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация (пока захардкодим, позже перенесем в .env)
FILES_ROOT = Path("../samples")  # Временно используем samples для тестов

# ============================================================================
# Модели данных
# ============================================================================

class FileInfo(BaseModel):
    """Информация о файле письма"""
    name: str
    url: str
    ext: str

class CurrentCard(BaseModel):
    """Текущая карточка для обработки"""
    card_id: int
    title: str
    incoming_no: int
    files: List[FileInfo]

class AppState(BaseModel):
    """Состояние приложения"""
    queue_count: int
    deferred_count: int
    assigned_session_count: int
    current_card: Optional[CurrentCard]

class AssignRequest(BaseModel):
    """Запрос на назначение исполнителя"""
    card_id: int
    owner_id: int
    co_owner_ids: List[int] = []
    comment_text: str = ""
    multi: bool = False

class SkipRequest(BaseModel):
    """Запрос на пропуск письма"""
    card_id: int

# ============================================================================
# Моковые данные для ЭТАПА 1
# ============================================================================

# Мокируем текущее состояние
MOCK_STATE = {
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
            },
            {
                "name": "test_document.html",
                "url": "/files/1233/test_document.html",
                "ext": "html"
            }
        ]
    }
}

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "app": "Kaiten Inbox API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "state": "/api/state",
            "assign": "/api/assign",
            "skip": "/api/skip",
            "undo": "/api/undo",
            "files": "/files/{incoming_no}/{filename}"
        }
    }

@app.get("/api/state", response_model=AppState)
async def get_state():
    """
    Получить текущее состояние очереди
    
    Returns:
        AppState: Текущее состояние с очередью, счетчиками и текущей карточкой
    """
    return MOCK_STATE

@app.post("/api/assign", response_model=AppState)
async def assign_card(request: AssignRequest):
    """
    Назначить исполнителя на карточку
    
    Args:
        request: Данные о назначении
        
    Returns:
        AppState: Обновленное состояние
    """
    # На ЭТАПЕ 1 просто возвращаем моковые данные
    print(f"[MOCK] Assign card {request.card_id} to user {request.owner_id}")
    if request.comment_text:
        print(f"[MOCK] Comment: {request.comment_text}")
    if request.co_owner_ids:
        print(f"[MOCK] Co-owners: {request.co_owner_ids}")
    
    return MOCK_STATE

@app.post("/api/skip", response_model=AppState)
async def skip_card(request: SkipRequest):
    """
    Пропустить текущую карточку (Skip)
    
    Args:
        request: ID карточки для пропуска
        
    Returns:
        AppState: Обновленное состояние
    """
    # На ЭТАПЕ 1 просто возвращаем моковые данные
    print(f"[MOCK] Skip card {request.card_id}")
    return MOCK_STATE

@app.post("/api/undo", response_model=AppState)
async def undo_last_action():
    """
    Отменить последнее действие
    
    Returns:
        AppState: Обновленное состояние
    """
    # На ЭТАПЕ 1 просто возвращаем моковые данные
    print(f"[MOCK] Undo last action")
    return MOCK_STATE

@app.get("/files/{incoming_no}/{filename}")
async def get_file(incoming_no: int, filename: str):
    """
    Получить файл письма
    
    Args:
        incoming_no: Входящий номер письма
        filename: Имя файла
        
    Returns:
        FileResponse: Файл для скачивания/просмотра
    """
    # Защита от path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Формируем путь к файлу
    # На ЭТАПЕ 1 используем папку samples напрямую (без подпапок)
    file_path = FILES_ROOT / filename
    
    # Проверяем существование файла
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Отдаем файл
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

# ============================================================================
# Запуск приложения
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
