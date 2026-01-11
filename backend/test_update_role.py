import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
user1 = 879380  # Горская - сделаем type: 2
user2 = 888238  # Бейгель - останется type: 1

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("ПРАВИЛЬНЫЙ способ: Update member role")
print("="*60)

url = f"{base_url}/cards/{card_id}"
url_members = f"{base_url}/cards/{card_id}/members"

# Шаг 1: Очистка
print("\n1. Очищаем members")
resp = client.get(url)
for m in resp.json().get('members', []):
    client.delete(f"{url}/members/{m['user_id']}")
print("   ✓ Очищено")

# Шаг 2: Добавляем первого пользователя
print(f"\n2. Добавляем {user1} (Горская)")
data = {"user_id": user1}
resp = client.post(url_members, json=data)
print(f"   POST status: {resp.status_code}")

# Шаг 3: Меняем role на type: 2
print(f"\n3. Меняем role на type: 2")
url_update = f"{url}/members/{user1}"
data_role = {"type": 2}
resp = client.patch(url_update, json=data_role)
print(f"   PATCH status: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.text}")

# Шаг 4: Добавляем второго пользователя (type: 1 по умолчанию)
print(f"\n4. Добавляем {user2} (Бейгель) с type: 1")
data = {"user_id": user2}
resp = client.post(url_members, json=data)
print(f"   POST status: {resp.status_code}")

# Шаг 5: Проверка
print("\n5. ИТОГОВЫЙ РЕЗУЛЬТАТ:")
resp = client.get(url)
card = resp.json()

print(f"   Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    type_label = "ОТВЕТСТВЕННЫЙ ✓" if m.get('type') == 2 else "Участник"
    print(f"     - {m.get('full_name')} (Type: {m.get('type')} - {type_label})")

client.close()
print("\n" + "="*60)
