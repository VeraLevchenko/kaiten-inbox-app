import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
card_id = 59536786  # Тестовая карточка
column_queue_id = int(os.getenv("KAITEN_COLUMN_QUEUE_ID"))  # 5592671
column_assign_id = int(os.getenv("KAITEN_COLUMN_ASSIGN_ID"))  # 5592672

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("=" * 60)
print("Тест перемещения карточки")
print("=" * 60)

# Получаем текущее состояние карточки
url = f"{base_url}/cards/{card_id}"
resp = client.get(url)
if resp.status_code == 200:
    card = resp.json()
    print(f"Card ID: {card.get('id')}")
    print(f"Title: {card.get('title')}")
    print(f"Current Column ID: {card.get('column_id')}")
    print(f"Current Lane ID: {card.get('lane_id')}")
    print(f"Current Owner ID: {card.get('owner_id')}")

# Перемещаем карточку в колонку "Назначить исполнителя"
print(f"\nПеремещаем в колонку {column_assign_id}...")

data = {
    "column_id": column_assign_id
}

resp = client.patch(url, json=data)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    print("✅ Карточка успешно перемещена!")
    result = resp.json()
    print(f"New Column ID: {result.get('column_id')}")
else:
    print(f"❌ Ошибка: {resp.text}")

# Проверяем финальное состояние
print("\nПроверяем финальное состояние...")
resp = client.get(url)
if resp.status_code == 200:
    card = resp.json()
    print(f"Column ID: {card.get('column_id')}")
    
# Возвращаем карточку обратно в очередь
print(f"\nВозвращаем карточку обратно в колонку {column_queue_id}...")
data = {"column_id": column_queue_id}
resp = client.patch(url, json=data)
if resp.status_code == 200:
    print("✅ Карточка возвращена в очередь")
else:
    print(f"❌ Ошибка возврата: {resp.text}")

client.close()
