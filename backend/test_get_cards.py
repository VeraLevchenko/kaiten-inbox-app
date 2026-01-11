import httpx
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("KAITEN_BASE_URL")
token = os.getenv("KAITEN_TOKEN")
board_id = int(os.getenv("KAITEN_BOARD_ID"))
column_id = int(os.getenv("KAITEN_COLUMN_QUEUE_ID"))
property_incoming_no = os.getenv("KAITEN_PROPERTY_INCOMING_NO")

client = httpx.Client(
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    timeout=30.0
)

print("="*60)
print("GET /cards с параметрами фильтрации")
print("="*60)

# Правильный endpoint с параметрами
url = f"{base_url}/cards"
params = {
    "board_id": board_id,
    "column_id": column_id,
    "condition": 1  # 1 - на доске, 2 - архив
}

print(f"URL: {url}")
print(f"Params: {params}")

try:
    response = client.get(url, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        cards = response.json()
        print(f"✅ Получено карточек: {len(cards)}")
        
        if cards:
            print("\n" + "="*60)
            print("Карточки в колонке:")
            print("="*60)
            
            for i, card in enumerate(cards, 1):
                print(f"\n{i}. Card ID: {card.get('id')}")
                print(f"   Title: {card.get('title')}")
                print(f"   Column ID: {card.get('column_id')}")
                
                props = card.get('properties', {})
                incoming_no = props.get(property_incoming_no)
                print(f"   Incoming No: {incoming_no}")
                
                if incoming_no:
                    try:
                        incoming_no_int = int(str(incoming_no).strip())
                        print(f"   ✅ Валидный номер: {incoming_no_int}")
                    except:
                        print(f"   ❌ Невалидный номер")
        else:
            print("⚠️ Карточек не найдено")
    else:
        print(f"❌ Ошибка {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

client.close()
