import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

# Получаем карточку которую ты добавила
card_id = 59536786
url = f"{base_url}/cards/{card_id}"

response = client.get(url)
if response.status_code == 200:
    card = response.json()
    print("Информация о карточке:")
    print(f"ID: {card.get('id')}")
    print(f"Title: {card.get('title')}")
    print(f"Board ID: {card.get('board_id')}")
    print(f"Lane ID: {card.get('lane_id')}")
    print(f"Column ID: {card.get('column_id')}")
    print(f"Properties: {card.get('properties')}")
    
    # Теперь попробуем получить карточки через lane
    board_id = card.get('board_id')
    lane_id = card.get('lane_id')
    column_id = card.get('column_id')
    
    print("\n" + "="*60)
    print(f"Пробуем получить карточки из колонки...")
    print("="*60)
    
    # Вариант 1: через lane
    url1 = f"{base_url}/boards/{board_id}/lanes/{lane_id}/columns/{column_id}/cards"
    print(f"\nВариант 1: {url1}")
    try:
        resp = client.get(url1)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ Работает! Карточек: {len(resp.json())}")
        else:
            print(f"❌ Не работает: {resp.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Вариант 2: напрямую через column
    url2 = f"{base_url}/columns/{column_id}/cards"
    print(f"\nВариант 2: {url2}")
    try:
        resp = client.get(url2)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ Работает! Карточек: {len(resp.json())}")
        else:
            print(f"❌ Не работает: {resp.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

client.close()
