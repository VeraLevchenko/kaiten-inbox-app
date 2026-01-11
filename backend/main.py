"""
Kaiten Inbox App - Backend
FastAPI приложение для распределения входящих писем
ЭТАП 5 (финальная версия) + Авторизация
"""

from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path
from dotenv import load_dotenv

# Импортируем модули
from kaiten_client import get_kaiten_client
import auth

# Загружаем переменные окружения
load_dotenv()

# Инициализация FastAPI
app = FastAPI(title="Kaiten Inbox API", version="1.0.0")

# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"[ERROR] Validation error:")
    print(f"  URL: {request.url}")
    body = await request.body()
    print(f"  Body: {body.decode('utf-8')}")
    print(f"  Errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# CORS для работы с React frontend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация из .env
FILES_ROOT = Path(os.getenv("FILES_ROOT", "../samples"))

# Счётчик назначенных карточек за сессию
assigned_session_count = 0

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
# Функции авторизации
# ============================================================================

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Получить текущего пользователя из токена"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    username = auth.verify_token(token)
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return username

# ============================================================================
# Вспомогательные функции
# ============================================================================

def get_files_for_card(incoming_no: int) -> List[FileInfo]:
    """
    Получить список файлов для карточки по входящему номеру
    
    Args:
        incoming_no: Входящий номер письма
        
    Returns:
        List[FileInfo]: Список файлов
    """
    files = []
    
    # Путь к папке с файлами письма
    card_folder = FILES_ROOT / str(incoming_no)
    
    # Проверяем существование папки
    if not card_folder.exists() or not card_folder.is_dir():
        print(f"[WARN] Folder not found: {card_folder}")
        return files
    
    # Получаем все файлы из папки
    try:
        for file_path in card_folder.iterdir():
            if file_path.is_file():
                # Получаем расширение файла
                ext = file_path.suffix.lstrip('.').lower()
                
                # Игнорируем служебные файлы
                if file_path.name.startswith('.'):
                    continue
                
                # Создаем FileInfo
                files.append(FileInfo(
                    name=file_path.name,
                    url=f"/files/{incoming_no}/{file_path.name}",
                    ext=ext if ext else "unknown"
                ))
        
        # Сортируем файлы по имени для стабильности
        files.sort(key=lambda f: f.name)
        
        print(f"[INFO] Found {len(files)} files for incoming_no {incoming_no}")
    except Exception as e:
        print(f"[ERROR] Failed to list files in {card_folder}: {e}")
    
    return files

def build_app_state() -> AppState:
    """
    Построить текущее состояние приложения на основе данных из Kaiten
    
    Returns:
        AppState: Состояние приложения
    """
    global assigned_session_count
    
    client = get_kaiten_client()
    
    # Получаем карточки из очереди с входящим номером
    queue_cards = client.get_queue_cards_with_incoming_no()
    
    # Счётчики
    queue_count = len(queue_cards)
    deferred_count = 0  # TODO: ЭТАП 6
    
    # Текущая карточка = первая в очереди (минимальный incoming_no)
    current_card = None
    if queue_cards:
        first_card = queue_cards[0]
        incoming_no = first_card["_incoming_no"]
        
        # Получаем файлы для карточки из реальной папки
        files = get_files_for_card(incoming_no)
        
        current_card = CurrentCard(
            card_id=first_card["id"],
            title=first_card["title"],
            incoming_no=incoming_no,
            files=files
        )
    
    return AppState(
        queue_count=queue_count,
        deferred_count=deferred_count,
        assigned_session_count=assigned_session_count,
        current_card=current_card
    )

# ============================================================================
# API Endpoints - Публичные (без авторизации)
# ============================================================================

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "app": "Kaiten Inbox API",
        "version": "1.0.0 - ЭТАП 5 + Auth",
        "status": "running",
        "endpoints": {
            "login": "/api/login",
            "logout": "/api/logout",
            "verify": "/api/verify",
            "state": "/api/state",
            "assign": "/api/assign",
            "skip": "/api/skip",
            "undo": "/api/undo",
            "files": "/files/{incoming_no}/{filename}"
        },
        "kaiten_connected": True,
        "files_root": str(FILES_ROOT),
        "assigned_this_session": assigned_session_count
    }

@app.post("/api/login")
async def login(credentials: dict):
    """
    Авторизация пользователя
    
    Body: {"username": "lvs", "password": "763202"}
    """
    username = credentials.get("username")
    password = credentials.get("password")
    
    if auth.verify_credentials(username, password):
        token = auth.create_session(username)
        return {
            "success": True,
            "token": token,
            "username": username
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

@app.post("/api/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Выход из системы"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        auth.delete_session(token)
    return {"success": True}

@app.get("/api/verify")
async def verify(authorization: Optional[str] = Header(None)):
    """Проверка токена сессии"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    username = auth.verify_token(token)
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"username": username}

@app.get("/api/public-url")
async def get_public_url():
    """Вернуть публичный URL backend для внешних сервисов"""
    public_url = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    return {"public_url": public_url}

# ============================================================================
# API Endpoints - Защищённые (требуют авторизацию)
# ============================================================================

@app.get("/api/state", response_model=AppState)
async def get_state(username: str = Depends(get_current_user)):
    """
    Получить текущее состояние очереди
    
    Returns:
        AppState: Текущее состояние с очередью, счетчиками и текущей карточкой
    """
    try:
        state = build_app_state()
        return state
    except Exception as e:
        print(f"[ERROR] Failed to build app state: {e}")
        import traceback
        traceback.print_exc()
        # В случае ошибки возвращаем пустое состояние
        return AppState(
            queue_count=0,
            deferred_count=0,
            assigned_session_count=assigned_session_count,
            current_card=None
        )

@app.post("/api/assign", response_model=AppState)
async def assign_card(request: AssignRequest, username: str = Depends(get_current_user)):
    """
    Назначить исполнителя на карточку
    ЭТАП 5 (final): Назначение через members с правильными roles
    
    Логика:
    1. Удалить всех текущих members
    2. Добавить первого исполнителя как member
    3. Изменить его роль на type: 2 (ответственный)
    4. Добавить остальных как members с type: 1 (участники)
    5. Добавить комментарий, если есть
    6. Переместить карточку в колонку "Назначить исполнителя"
    7. Проверить и удалить лишних members
    
    Args:
        request: Данные о назначении
        
    Returns:
        AppState: Обновленное состояние
    """
    global assigned_session_count
    
    client = get_kaiten_client()
    
    try:
        print("="*60)
        print(f"[INFO] ===== STARTING ASSIGNMENT =====")
        print(f"[INFO] Card ID: {request.card_id}")
        print(f"[INFO] Owner (type: 2): {request.owner_id}")
        print(f"[INFO] Co-owners (type: 1): {request.co_owner_ids}")
        print("="*60)
        
        # Шаг 1: Удалить всех текущих members
        print(f"\n[STEP 1] Removing all existing members...")
        success = client.remove_all_members(request.card_id)
        print(f"[STEP 1] Result: {'SUCCESS' if success else 'FAILED'}")
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove existing members")
        
        # Шаг 2: Добавить первого исполнителя как member
        print(f"\n[STEP 2] Adding primary member {request.owner_id}...")
        success = client.add_card_member(request.card_id, request.owner_id)
        print(f"[STEP 2] Result: {'SUCCESS' if success else 'FAILED'}")
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add primary member")
        
        # Шаг 3: Изменить его роль на type: 2
        print(f"\n[STEP 3] Updating member role to type: 2...")
        success = client.update_member_role(request.card_id, request.owner_id, 2)
        print(f"[STEP 3] Result: {'SUCCESS' if success else 'FAILED'}")
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update member role")
        
        # Шаг 4: Добавить co-owners
        if request.co_owner_ids:
            print(f"\n[STEP 4] Adding {len(request.co_owner_ids)} co-owners...")
            for co_owner_id in request.co_owner_ids:
                print(f"  Adding co-owner {co_owner_id}...")
                client.add_card_member(request.card_id, co_owner_id)
        
        # Шаг 5: Комментарий
        if request.comment_text and request.comment_text.strip():
            print(f"\n[STEP 5] Adding comment...")
            client.add_comment(request.card_id, request.comment_text)
        
        # Шаг 6: Переместить карточку
        print(f"\n[STEP 6] Moving card to column...")
        column_assign_id = int(os.getenv("KAITEN_COLUMN_ASSIGN_ID"))
        success = client.move_card(request.card_id, column_assign_id)
        print(f"[STEP 6] Result: {'SUCCESS' if success else 'FAILED'}")
        if not success:
            raise HTTPException(status_code=500, detail="Failed to move card")
        
        # ========== ШАГ 7: ПРОВЕРКА MEMBERS ==========
        print(f"\n[STEP 7] Verifying members...")
        card = client.get_card(request.card_id)
        if card:
            members = card.get('members', [])
            print(f"  Total members: {len(members)}")
            
            # Список разрешённых user_id
            allowed_ids = {request.owner_id} | set(request.co_owner_ids)
            print(f"  Expected members: {allowed_ids}")
            
            # Список лишних для удаления
            to_remove = []
            
            # Проверяем каждого member
            for member in members:
                user_id = member.get('user_id')
                member_type = member.get('type')
                full_name = member.get('full_name')
                
                if user_id in allowed_ids:
                    print(f"  ✅ {full_name} (ID: {user_id}, Type: {member_type}) - OK")
                else:
                    print(f"  ⚠️  UNEXPECTED: {full_name} (ID: {user_id}, Type: {member_type})")
                    to_remove.append((user_id, full_name))
            
            # ========== ШАГ 8: УДАЛИТЬ ЛИШНИХ ==========
            if to_remove:
                print(f"\n[STEP 8] Removing {len(to_remove)} unexpected members...")
                for user_id, full_name in to_remove:
                    print(f"  Removing {full_name} (ID: {user_id})...")
                    url = f"{client.base_url}/cards/{request.card_id}/members/{user_id}"
                    try:
                        response = client.client.delete(url)
                        if response.status_code in [200, 404]:
                            print(f"    ✅ Removed")
                        else:
                            print(f"    ⚠️  Status: {response.status_code}")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
        
        assigned_session_count += 1
        
        print(f"\n[SUCCESS] ===== ASSIGNMENT COMPLETE =====")
        print(f"[SUCCESS] Total assigned: {assigned_session_count}")
        print("="*60)
        
        return build_app_state()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n[ERROR] ===== ASSIGNMENT FAILED =====")
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        raise HTTPException(status_code=500, detail=f"Failed to assign card: {str(e)}")

@app.post("/api/skip", response_model=AppState)
async def skip_card(request: SkipRequest, username: str = Depends(get_current_user)):
    """
    Пропустить текущую карточку (Skip)
    TODO: ЭТАП 6
    
    Args:
        request: ID карточки для пропуска
        
    Returns:
        AppState: Обновленное состояние
    """
    print(f"[TODO ЭТАП 6] Skip card {request.card_id}")
    return build_app_state()

@app.post("/api/undo", response_model=AppState)
async def undo_last_action(username: str = Depends(get_current_user)):
    """
    Отменить последнее действие
    TODO: ЭТАП 6
    
    Returns:
        AppState: Обновленное состояние
    """
    print(f"[TODO ЭТАП 6] Undo last action")
    return build_app_state()

@app.get("/files/{incoming_no}/{filename}")
async def get_file(
    incoming_no: int, 
    filename: str, 
    token: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Получить файл письма для просмотра в браузере
    Поддерживает авторизацию через ?token=XXX или Authorization header
    
    Args:
        incoming_no: Входящий номер письма
        filename: Имя файла
        token: Опциональный токен авторизации через query parameter
        
    Returns:
        FileResponse: Файл для просмотра
    """
    import mimetypes
    import urllib.parse
    
    # Если токен передан через URL - проверяем его
    if token:
        verified_username = auth.verify_token(token)
        if not verified_username:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        # Используем username из токена
        username = verified_username
    # Иначе username уже проверен через Depends(get_current_user)
    
    # Защита от path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Формируем путь к файлу
    file_path = FILES_ROOT / str(incoming_no) / filename
    
    # Проверяем существование
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    # Определяем расширение
    ext = file_path.suffix.lower()
    
    # Определяем MIME-тип
    mime_type, _ = mimetypes.guess_type(filename)
    
    # Специальная обработка для разных типов файлов
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        # Изображения - показываем inline
        mime_type = mime_type or 'image/jpeg'
        disposition = 'inline'
    elif ext == '.pdf':
        # PDF - показываем inline
        mime_type = 'application/pdf'
        disposition = 'inline'
    elif ext in ['.txt', '.log', '.csv']:
        # Текстовые файлы - показываем inline
        mime_type = 'text/plain; charset=utf-8'
        disposition = 'inline'
    elif ext == '.html':
        # HTML - показываем inline
        mime_type = 'text/html; charset=utf-8'
        disposition = 'inline'
    elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
        # Office документы - предлагаем скачать
        mime_type = mime_type or 'application/octet-stream'
        disposition = 'attachment'
    else:
        # Остальные - скачивание
        mime_type = mime_type or 'application/octet-stream'
        disposition = 'attachment'
    
    print(f"[DEBUG] Serving file: {incoming_no}/{filename}, MIME: {mime_type}, Disposition: {disposition}")
    
    # Кодируем имя файла
    encoded_filename = urllib.parse.quote(filename)
    
    # Формируем заголовок
    if disposition == 'inline':
        content_disposition = f"inline; filename*=UTF-8''{encoded_filename}"
    else:
        content_disposition = f"attachment; filename*=UTF-8''{encoded_filename}"
    
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        headers={
            "Content-Disposition": content_disposition
        }
    )

@app.get("/public-files/{incoming_no}/{filename}")
async def get_public_file(incoming_no: int, filename: str):
    """
    Публичный доступ к файлам для внешних viewers (Google Docs, Office Online)
    БЕЗ авторизации - используется только для просмотра через iframe
    """
    import mimetypes
    import urllib.parse
    
    # Защита от path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Формируем путь к файлу
    file_path = FILES_ROOT / str(incoming_no) / filename
    
    # Проверяем существование
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    # Определяем MIME-тип
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or 'application/octet-stream'
    
    # Кодируем имя файла
    encoded_filename = urllib.parse.quote(filename)
    
    print(f"[DEBUG] Public file request: {incoming_no}/{filename}")
    
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"
        }
    )

# ============================================================================
# Запуск приложения
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Получаем параметры из .env
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    
    print(f"🚀 Starting Kaiten Inbox Backend (ЭТАП 5 + Auth)")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"📁 Files root: {FILES_ROOT}")
    print(f"✅ Members-based assignment enabled!")
    print(f"🔒 Authentication enabled: {auth.VALID_USERNAME}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )