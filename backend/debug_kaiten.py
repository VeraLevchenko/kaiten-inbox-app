import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# Получаем настройки
base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
column_queue_id = int(os.getenv("KAITEN_COLUMN_QUEUE_ID"))
property_incoming_no = os.getenv("KAITEN_PROPERTY_INCOMING_NO")

print("=" * 60)
print("Проверка подключения к Kaiten API")
print("=" * 60)
print(f"Base URL: {base_url}")
print(f"Token: {token[:20]}..." if token else "Token: NOT SET")
print(f"Board ID: {board_id}")
print(f"Column Queue ID: {column_queue_id}")
print(f"Property Incoming No: {property_incoming_no}")
print("=" * 60)

# Создаем HTTP клиент
client = httpx.Client(
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    timeout=30.0
)

# Запрос карточек из колонки
url = f"{base_url}/boards/{board_id}/columns/{column_queue_id}/cards"
print(f"\n📡 Запрос: {url}")

try:
    response = client.get(url)
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        cards = response.json()
        print(f"📦 Получено карточек: {len(cards)}")
        
        if cards:
            print("\n" + "=" * 60)
            print("Карточки в колонке:")
            print("=" * 60)
            
            for i, card in enumerate(cards, 1):
                print(f"\n{i}. Card ID: {card.get('id')}")
                print(f"   Title: {card.get('title')}")
                print(f"   Column ID: {card.get('column_id')}")
                
                # Проверяем properties
                props = card.get('properties', {})
                incoming_no = props.get(property_incoming_no)
                print(f"   Properties: {list(props.keys())}")
                print(f"   Incoming No ({property_incoming_no}): {incoming_no}")
                
                if incoming_no:
                    try:
                        incoming_no_int = int(str(incoming_no).strip())
                        print(f"   ✅ Валидный входящий номер: {incoming_no_int}")
                    except (ValueError, TypeError) as e:
                        print(f"   ❌ Невалидный входящий номер: {e}")
        else:
            print("\n⚠️ В колонке нет карточек!")
            print("\nВозможные причины:")
            print("1. Карточки находятся в другой колонке")
            print("2. Неправильный KAITEN_COLUMN_QUEUE_ID в .env")
            print("3. У карточек нет доступа через API")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Ошибка при запросе: {e}")

client.close()
print("\n" + "=" * 60)
EOF
cat /tmp/debug_kaiten.py
Output

# Скрипт для отладки подключения к Kaiten API

import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# Получаем настройки
base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
column_queue_id = int(os.getenv("KAITEN_COLUMN_QUEUE_ID"))
property_incoming_no = os.getenv("KAITEN_PROPERTY_INCOMING_NO")

print("=" * 60)
print("Проверка подключения к Kaiten API")
print("=" * 60)
print(f"Base URL: {base_url}")
print(f"Token: {token[:20]}..." if token else "Token: NOT SET")
print(f"Board ID: {board_id}")
print(f"Column Queue ID: {column_queue_id}")
print(f"Property Incoming No: {property_incoming_no}")
print("=" * 60)

# Создаем HTTP клиент
client = httpx.Client(
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    timeout=30.0
)

# Запрос карточек из колонки
url = f"{base_url}/boards/{board_id}/columns/{column_queue_id}/cards"
print(f"\n📡 Запрос: {url}")

try:
    response = client.get(url)
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        cards = response.json()
        print(f"📦 Получено карточек: {len(cards)}")
        
        if cards:
            print("\n" + "=" * 60)
            print("Карточки в колонке:")
            print("=" * 60)
            
            for i, card in enumerate(cards, 1):
                print(f"\n{i}. Card ID: {card.get('id')}")
                print(f"   Title: {card.get('title')}")
                print(f"   Column ID: {card.get('column_id')}")
                
                # Проверяем properties
                props = card.get('properties', {})
                incoming_no = props.get(property_incoming_no)
                print(f"   Properties: {list(props.keys())}")
                print(f"   Incoming No ({property_incoming_no}): {incoming_no}")
                
                if incoming_no:
                    try:
                        incoming_no_int = int(str(incoming_no).strip())
                        print(f"   ✅ Валидный входящий номер: {incoming_no_int}")
                    except (ValueError, TypeError) as e:
                        print(f"   ❌ Невалидный входящий номер: {e}")
        else:
            print("\n⚠️ В колонке нет карточек!")
            print("\nВозможные причины:")
            print("1. Карточки находятся в другой колонке")
            print("2. Неправильный KAITEN_COLUMN_QUEUE_ID в .env")
            print("3. У карточек нет доступа через API")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Ошибка при запросе: {e}")

client.close()
print("\n" + "=" * 60)