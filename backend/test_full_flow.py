import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")

card_id = 59536786
new_responsible = 531591  # Забелин

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("Полный тест процесса назначения")
print("="*60)

url = f"{base_url}/cards/{card_id}"

# ШАГ 0: Начальное состояние
print("\n0. НАЧАЛЬНОЕ СОСТОЯНИЕ:")
resp = client.get(url)
card = resp.json()
print(f"   Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

# ШАГ 1: Удаляем всех members
print("\n1. УДАЛЯЕМ ВСЕХ MEMBERS:")
members = card.get('members', [])
for m in members:
    user_id = m.get('user_id')
    print(f"   Удаляем {m.get('full_name')} (ID: {user_id})")
    url_del = f"{url}/members/{user_id}"
    resp_del = client.delete(url_del)
    print(f"     Status: {resp_del.status_code}")

# Проверка после удаления
resp = client.get(url)
card = resp.json()
print(f"\n   После удаления - Members: {len(card.get('members', []))}")
if card.get('members'):
    print("   ❌ ОСТАЛИСЬ MEMBERS:")
    for m in card.get('members', []):
        print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')})")

# ШАГ 2: Добавляем нового member
print(f"\n2. ДОБАВЛЯЕМ НОВОГО MEMBER (ID: {new_responsible}):")
url_members = f"{base_url}/cards/{card_id}/members"
data = {"user_id": new_responsible}
resp = client.post(url_members, json=data)
print(f"   Status: {resp.status_code}")

# ШАГ 3: Меняем роль на type: 2
print(f"\n3. МЕНЯЕМ РОЛЬ НА TYPE: 2:")
url_update = f"{url}/members/{new_responsible}"
data = {"type": 2}
resp = client.patch(url_update, json=data)
print(f"   Status: {resp.status_code}")

# ШАГ 4: Финальная проверка
print("\n4. ФИНАЛЬНОЕ СОСТОЯНИЕ:")
resp = client.get(url)
card = resp.json()
print(f"   Owner: {card.get('owner', {}).get('full_name')} (ID: {card.get('owner_id')})")
print(f"   Members: {len(card.get('members', []))}")
for m in card.get('members', []):
    type_label = "ОТВЕТСТВЕННЫЙ" if m.get('type') == 2 else "Участник"
    print(f"     - {m.get('full_name')} (ID: {m.get('user_id')}, Type: {m.get('type')} - {type_label})")

client.close()
print("\n" + "="*60)
