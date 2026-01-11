import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
new_owner = 879380  # Горская - будет ответственным (type: 2)
co_owner = 888238   # Бейгель - будет участником (type: 1)

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("ПРАВИЛЬНАЯ логика назначения")
print("="*60)

url = f"{base_url}/cards/{card_id}"

# Шаг 1: Очистить members
print("\n1. Очищаем members")
resp = client.get(url)
card = resp.json()
for m in card.get('members', []):
    client.delete(f"{base_url}/cards/{card_id}/members/{m['user_id']}")
print("   ✓ Очищено")

# Шаг 2: Назначить owner_id
print(f"\n2. Назначаем owner_id = {new_owner} (Горская)")
data = {"owner_id": new_owner}
resp = client.patch(url, json=data)
print(f"   Status: {resp.status_code}")

# Шаг 3: Добавить co-owners
print(f"\n3. Добавляем участника {co_owner} (Бейгель)")
url_members = f"{base_url}/cards/{card_id}/members"
data = {"user_id": co_owner}
resp = client.post(url_members, json=data)
print(f"   Status: {resp.status_code}")

# Шаг 4: Проверка
print("\n4. РЕЗУЛЬТАТ:")
resp = client.get(url)
card = resp.json()

print(f"   Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    type_label = "ОТВЕТСТВЕННЫЙ" if m.get('type') == 2 else "Участник"
    print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')} - {type_label})")

client.close()
print("\n" + "="*60)
