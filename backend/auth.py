"""
Модуль авторизации
Простая проверка логин/пароль с сессиями
"""

import os
from typing import Optional
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv

load_dotenv()

# Учетные данные
VALID_USERNAME = os.getenv("AUTH_USERNAME")
VALID_PASSWORD = os.getenv("AUTH_PASSWORD")

# Простое хранилище активных сессий (в памяти)
# В production лучше использовать Redis или БД
active_sessions = {}

def generate_token() -> str:
    """Генерация случайного токена сессии"""
    return secrets.token_urlsafe(32)

def create_session(username: str) -> str:
    """Создать новую сессию"""
    token = generate_token()
    active_sessions[token] = {
        "username": username,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=8)  # Сессия на 8 часов
    }
    print(f"[AUTH] Session created for {username}: {token[:10]}...")
    return token

def verify_credentials(username: str, password: str) -> bool:
    """Проверка логина и пароля"""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def verify_token(token: Optional[str]) -> Optional[str]:
    """Проверка токена сессии. Возвращает username или None"""
    if not token:
        return None
    
    session = active_sessions.get(token)
    if not session:
        return None
    
    # Проверяем срок действия
    if datetime.now() > session["expires_at"]:
        # Сессия истекла
        del active_sessions[token]
        print(f"[AUTH] Session expired: {token[:10]}...")
        return None
    
    return session["username"]

def delete_session(token: str):
    """Удалить сессию (logout)"""
    if token in active_sessions:
        username = active_sessions[token]["username"]
        del active_sessions[token]
        print(f"[AUTH] Session deleted for {username}")