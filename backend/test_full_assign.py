import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
card_id = 59536786
owner_id = 488861  # Габидулина

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("=" * 60)
print("Полный тест назначения исполнителя")
print("=" * 60)

url = f"{base_url}/cards/{card_id}"

# Шаг 1: Назначить owner
print(f"\n1. Назначаем owner_id = {owner_id} (Габидулина)")
data = {"owner_id": owner_id}
resp = client.patch(url, json=data)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print("   ✅ Owner назначен")
else:
    print(f"   ❌ Ошибка: {resp.text}")

# Шаг 2: Переместить в колонку "Назначить исполнителя"
print(f"\n2. Перемещаем в колонку 5592672")
data = {"column_id": 5592672}
resp = client.patch(url, json=data)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print("   ✅ Карточка перемещена")
else:
    print(f"   ❌ Ошибка: {resp.text}")

# Шаг 3: Проверяем финальное состояние
print(f"\n3. Проверяем финальное состояние")
resp = client.get(url)
if resp.status_code == 200:
    card = resp.json()
    print(f"   Owner ID: {card.get('owner_id')}")
    print(f"   Owner: {card.get('owner', {}).get('full_name')}")
    print(f"   Column ID: {card.get('column_id')}")
    print("   ✅ Всё корректно!")

# Возвращаем в исходное состояние
print(f"\n4. Возвращаем карточку в очередь")
data = {"column_id": 5592671}
resp = client.patch(url, json=data)
if resp.status_code == 200:
    print("   ✅ Карточка возвращена")

client.close()
print("\n" + "=" * 60)
print("Тест завершён!")
print("=" * 60)
