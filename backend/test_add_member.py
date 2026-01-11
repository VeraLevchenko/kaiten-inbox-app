import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
current_owner = 442909  # isogd.2019 (должен остаться owner)
new_member = 531591  # Забелин (добавить как member)

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("Тест: Добавление member без изменения owner")
print("="*60)

# Шаг 1: Текущее состояние
url = f"{base_url}/cards/{card_id}"
resp = client.get(url)
card = resp.json()

print(f"\nДО изменений:")
print(f"  Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"  Members: {len(card.get('members', []))}")

# Шаг 2: Добавляем member
print(f"\nДобавляем member {new_member} (Забелин)")
url_members = f"{base_url}/cards/{card_id}/members"
data = {"user_id": new_member}
resp = client.post(url_members, json=data)
print(f"  Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"  Error: {resp.text}")

# Шаг 3: Проверяем результат
resp = client.get(url)
card = resp.json()

print(f"\nПОСЛЕ изменений:")
print(f"  Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"  Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    print(f"    - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

client.close()
