import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
user1 = 879380  # Горская (type: 2 - ответственный)
user2 = 888238  # Бейгель (type: 1 - участник)

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("Тест добавления members с разными type")
print("="*60)

# ШАГ 1: ОЧИЩАЕМ ВСЕ MEMBERS
print("\n1. Очищаем всех members:")
url = f"{base_url}/cards/{card_id}"
resp = client.get(url)
card = resp.json()

members = card.get('members', [])
print(f"   Найдено members: {len(members)}")

for m in members:
    user_id = m.get('user_id')
    print(f"   Удаляем {m.get('full_name')} (ID: {user_id})")
    url_del = f"{base_url}/cards/{card_id}/members/{user_id}"
    resp_del = client.delete(url_del)
    print(f"     Status: {resp_del.status_code}")

print("   ✓ Все members удалены")

# Проверяем что members пусты
resp = client.get(url)
card = resp.json()
print(f"   Проверка: members = {len(card.get('members', []))}")

# ШАГ 2: Добавляем member с type: 2
print(f"\n2. Добавляем Горская (ID: {user1}) с type: 2")
url_members = f"{base_url}/cards/{card_id}/members"
data1 = {"user_id": user1, "type": 2}
resp1 = client.post(url_members, json=data1)
print(f"   Status: {resp1.status_code}")
if resp1.status_code != 200:
    print(f"   Error: {resp1.text[:300]}")

# ШАГ 3: Добавляем member с type: 1
print(f"\n3. Добавляем Бейгель (ID: {user2}) с type: 1")
data2 = {"user_id": user2, "type": 1}
resp2 = client.post(url_members, json=data2)
print(f"   Status: {resp2.status_code}")
if resp2.status_code != 200:
    print(f"   Error: {resp2.text[:300]}")

# ШАГ 4: Проверяем результат
print("\n4. Финальная проверка:")
resp = client.get(url)
card = resp.json()

print(f"   Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

client.close()
print("\n" + "="*60)
