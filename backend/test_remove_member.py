import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
old_user_id = 442909  # isogd.2019
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
print("Тест: Удаление старого member перед назначением owner")
print("="*60)

# Шаг 1: Удаляем старого пользователя из members
print(f"\n1. Удаляем user {old_user_id} из members")
url = f"{base_url}/cards/{card_id}/members/{old_user_id}"
resp = client.delete(url)
print(f"   Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Response: {resp.text}")

# Шаг 2: Назначаем нового owner
print(f"\n2. Назначаем owner_id = {new_owner_id}")
url = f"{base_url}/cards/{card_id}"
data = {"owner_id": new_owner_id}
resp = client.patch(url, json=data)
print(f"   Status: {resp.status_code}")

# Шаг 3: Проверяем результат
print(f"\n3. Проверяем результат:")
resp = client.get(url)
card = resp.json()

print(f"   Owner ID: {card.get('owner_id')}")
print(f"   Owner: {card.get('owner', {}).get('full_name')}")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

client.close()
