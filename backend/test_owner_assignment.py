import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
new_owner_id = 531591  # Забелин

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("Проверка назначения owner")
print("="*60)

# Шаг 1: Получаем текущее состояние
url = f"{base_url}/cards/{card_id}"
resp = client.get(url)
card = resp.json()

print(f"\nТекущее состояние:")
print(f"  Owner ID: {card.get('owner_id')}")
print(f"  Owner: {card.get('owner', {}).get('full_name')}")
print(f"  Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    print(f"    - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

# Шаг 2: Попробуем назначить нового owner
print(f"\nНазначаем owner_id = {new_owner_id} (Забелин)")
data = {"owner_id": new_owner_id}
resp = client.patch(url, json=data)

if resp.status_code == 200:
    print("✅ Запрос успешный")
    
    # Проверяем результат
    resp = client.get(url)
    card = resp.json()
    
    print(f"\nРезультат:")
    print(f"  Owner ID: {card.get('owner_id')}")
    print(f"  Owner: {card.get('owner', {}).get('full_name')}")
    print(f"  Members: {len(card.get('members', []))}")
    for m in card.get('members', []):
        print(f"    - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")
else:
    print(f"❌ Ошибка: {resp.status_code}")
    print(f"Response: {resp.text}")

client.close()
