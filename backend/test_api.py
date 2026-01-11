import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

# Тест 1: Получить карточки доски
print("=" * 60)
print("Тест 1: GET /boards/{board_id}/cards")
print("=" * 60)
url1 = f"{base_url}/boards/{board_id}/cards"
print(f"URL: {url1}")
try:
    response = client.get(url1)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        cards = response.json()
        print(f"✅ Получено карточек: {len(cards)}")
        if cards:
            print(f"\nПервая карточка:")
            card = cards[0]
            print(f"  ID: {card.get('id')}")
            print(f"  Title: {card.get('title')}")
            print(f"  Column ID: {card.get('column_id')}")
            print(f"  Properties: {card.get('properties', {})}")
    else:
        print(f"❌ Ошибка: {response.text}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "=" * 60)
print("Тест 2: GET /cards/{card_id}")
print("=" * 60)
url2 = f"{base_url}/cards/59536786"
print(f"URL: {url2}")
try:
    response = client.get(url2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        card = response.json()
        print(f"✅ Карточка получена:")
        print(f"  ID: {card.get('id')}")
        print(f"  Title: {card.get('title')}")
        print(f"  Column ID: {card.get('column_id')}")
        print(f"  Properties: {card.get('properties', {})}")
    else:
        print(f"❌ Ошибка: {response.text}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

client.close()
