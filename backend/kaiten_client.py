"""
Kaiten API Client
Класс для взаимодействия с API Kaiten
"""

import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class KaitenClient:
    """
    Клиент для работы с API Kaiten
    
    Основные методы:
    - get_queue_cards_with_incoming_no() - получить карточки очереди с входящим номером
    - get_card() - получить одну карточку по ID
    - move_card() - переместить карточку в другую колонку
    - add_comment() - добавить комментарий к карточке
    - add_card_member() - добавить участника
    - update_member_role() - изменить роль участника (type: 2 = ответственный)
    - remove_all_members() - удалить всех участников
    """
    
    def __init__(self):
        self.base_url = os.getenv("KAITEN_BASE_URL")
        self.token = os.getenv("KAITEN_TOKEN")
        self.board_id = int(os.getenv("KAITEN_BOARD_ID"))
        self.column_queue_id = int(os.getenv("KAITEN_COLUMN_QUEUE_ID"))
        self.column_assign_id = int(os.getenv("KAITEN_COLUMN_ASSIGN_ID"))
        self.property_incoming_no = os.getenv("KAITEN_PROPERTY_INCOMING_NO")
        
        # Настройка HTTP клиента
        self.client = httpx.Client(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            },
            timeout=30.0
        )
    
    def get_cards_from_column(self, column_id: int) -> List[Dict]:
        """
        Получить карточки из указанной колонки
        
        Args:
            column_id: ID колонки
            
        Returns:
            List[Dict]: Список карточек
        """
        try:
            # Правильный endpoint: GET /cards с параметрами
            url = f"{self.base_url}/cards"
            params = {
                "board_id": self.board_id,
                "column_id": column_id,
                "condition": 1  # 1 = на доске, 2 = архив
            }
            
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            cards = response.json()
            print(f"[INFO] Got {len(cards)} cards from column {column_id}")
            return cards
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to get cards from column {column_id}: {e}")
            return []
    
    def get_queue_cards_with_incoming_no(self) -> List[Dict]:
        """
        Получить карточки из колонки "Очередь" с входящим номером
        Фильтрует только карточки, у которых есть properties.id_228499
        
        Returns:
            List[Dict]: Отфильтрованные и отсортированные карточки
        """
        # Получаем карточки из колонки "Очередь"
        all_cards = self.get_cards_from_column(self.column_queue_id)
        
        # Фильтруем карточки с входящим номером
        filtered_cards = []
        
        for card in all_cards:
            # Проверяем наличие входящего номера в properties
            if "properties" in card and self.property_incoming_no in card["properties"]:
                incoming_no_value = card["properties"][self.property_incoming_no]
                
                # Проверяем что значение не пустое и можно преобразовать в число
                if incoming_no_value and str(incoming_no_value).strip():
                    try:
                        incoming_no = int(str(incoming_no_value).strip())
                        card["_incoming_no"] = incoming_no  # Сохраняем для сортировки
                        filtered_cards.append(card)
                        print(f"[DEBUG] Card {card.get('id')} - incoming_no: {incoming_no}, title: {card.get('title')}")
                    except (ValueError, TypeError):
                        # Игнорируем карточки с невалидным номером
                        print(f"[WARN] Card {card.get('id')} has invalid incoming_no: {incoming_no_value}")
                        continue
        
        # Сортируем по входящему номеру (возрастание)
        filtered_cards.sort(key=lambda x: x["_incoming_no"])
        
        print(f"[INFO] Found {len(filtered_cards)} cards in queue with incoming_no")
        return filtered_cards
    
    def get_card(self, card_id: int) -> Optional[Dict]:
        """
        Получить полную информацию о карточке по ID
        
        Args:
            card_id: ID карточки
            
        Returns:
            Dict: Данные карточки или None
        """
        try:
            url = f"{self.base_url}/cards/{card_id}"
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to get card {card_id}: {e}")
            return None
    
    def move_card(self, card_id: int, column_id: int) -> bool:
        """
        Переместить карточку в другую колонку
        
        Args:
            card_id: ID карточки
            column_id: ID целевой колонки
            
        Returns:
            bool: True если успешно
        """
        try:
            url = f"{self.base_url}/cards/{card_id}"
            data = {"column_id": column_id}
            
            response = self.client.patch(url, json=data)
            response.raise_for_status()
            
            print(f"[INFO] Card {card_id} moved to column {column_id}")
            return True
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to move card {card_id}: {e}")
            return False
    
    def add_card_member(self, card_id: int, user_id: int) -> bool:
        """
        Добавить участника (member) к карточке
        
        Args:
            card_id: ID карточки
            user_id: ID пользователя
            
        Returns:
            bool: True если успешно
        """
        try:
            url = f"{self.base_url}/cards/{card_id}/members"
            data = {"user_id": user_id}
            
            response = self.client.post(url, json=data)
            response.raise_for_status()
            
            print(f"[INFO] User {user_id} added as member to card {card_id}")
            return True
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to add member to card {card_id}: {e}")
            return False
    
    def update_member_role(self, card_id: int, user_id: int, role_type: int) -> bool:
        """
        Изменить роль участника карточки
        
        Args:
            card_id: ID карточки
            user_id: ID пользователя
            role_type: Тип роли (2 = ответственный, 1 = участник)
            
        Returns:
            bool: True если успешно
        """
        try:
            url = f"{self.base_url}/cards/{card_id}/members/{user_id}"
            data = {"type": role_type}
            
            response = self.client.patch(url, json=data)
            response.raise_for_status()
            
            role_name = "ответственный" if role_type == 2 else "участник"
            print(f"[INFO] User {user_id} role changed to {role_name} on card {card_id}")
            return True
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to update member role on card {card_id}: {e}")
            return False
    
    def remove_all_members(self, card_id: int) -> bool:
        """
        Удалить всех участников из карточки
        
        Args:
            card_id: ID карточки
            
        Returns:
            bool: True если успешно
        """
        try:
            # Получаем текущих members
            card = self.get_card(card_id)
            if not card:
                return False
            
            members = card.get('members', [])
            print(f"[INFO] Removing {len(members)} members from card {card_id}")
            
            for member in members:
                user_id = member.get('user_id')
                if user_id:
                    url = f"{self.base_url}/cards/{card_id}/members/{user_id}"
                    response = self.client.delete(url)
                    # 200 = успешно, 404 = уже удалён
                    if response.status_code not in [200, 404]:
                        response.raise_for_status()
            
            print(f"[INFO] All members removed from card {card_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to remove members from card {card_id}: {e}")
            return False
    
    def add_comment(self, card_id: int, text: str) -> bool:
        """
        Добавить комментарий к карточке
        
        Args:
            card_id: ID карточки
            text: Текст комментария
            
        Returns:
            bool: True если успешно
        """
        try:
            url = f"{self.base_url}/cards/{card_id}/comments"
            data = {"text": text}
            
            response = self.client.post(url, json=data)
            response.raise_for_status()
            
            print(f"[INFO] Comment added to card {card_id}")
            return True
        except httpx.HTTPError as e:
            print(f"[ERROR] Failed to add comment to card {card_id}: {e}")
            return False
    
    def close(self):
        """Закрыть HTTP клиент"""
        self.client.close()


# Singleton instance
_kaiten_client = None

def get_kaiten_client() -> KaitenClient:
    """Получить единственный экземпляр KaitenClient"""
    global _kaiten_client
    if _kaiten_client is None:
        _kaiten_client = KaitenClient()
    return _kaiten_client