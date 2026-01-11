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

# Получаем карточку чтобы посмотреть структуру
card_id = 59536786
print("=" * 60)
print("Получаем карточку для анализа")
print("=" * 60)

url = f"{base_url}/cards/{card_id}"
resp = client.get(url)
if resp.status_code == 200:
    card = resp.json()
    print(f"Card ID: {card.get('id')}")
    print(f"Title: {card.get('title')}")
    print(f"Current Owner ID: {card.get('owner_id')}")
    print(f"Current Owner: {card.get('owner', {}).get('full_name')}")
    
    # Проверяем members
    members = card.get('members', [])
    print(f"\nMembers ({len(members)}):")
    for m in members:
        print(f"  - {m.get('full_name')} (user_id: {m.get('user_id')}, type: {m.get('type')})")

# Пробуем назначить owner_id = 100001
print("\n" + "=" * 60)
print("Тест 1: owner_id = 100001")
print("=" * 60)

data = {"owner_id": 100001}
resp = client.patch(f"{base_url}/cards/{card_id}", json=data)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

# Если ошибка, попробуем реальный ID
if resp.status_code != 200:
    print("\n" + "=" * 60)
    print("Тест 2: Используем ID существующего пользователя")
    print("=" * 60)
    
    card_resp = client.get(f"{base_url}/cards/{card_id}")
    if card_resp.status_code == 200:
        card_data = card_resp.json()
        
        # Берём ID из members
        members = card_data.get('members', [])
        if members:
            test_user_id = members[0].get('user_id')
            print(f"Пробуем user_id: {test_user_id}")
            
            data2 = {"owner_id": test_user_id}
            resp2 = client.patch(f"{base_url}/cards/{card_id}", json=data2)
            print(f"Status: {resp2.status_code}")
            print(f"Response: {resp2.text[:500]}")

client.close()
