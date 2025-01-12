import os
import requests
import time
import json

HEADERS = {
    'User-Agent': 'TarotBot/1.0 (https://t.me/your_bot_username) Python/3.9'
}

NUMBER_NAMES = {
    1: "Ace",
    2: "Two",
    3: "Three", 
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten"
}

# Специальные хэши для карт, которые требуют особой обработки
SPECIAL_CARDS = {
    "Nine_of_Wands": "Tarot_Nine_of_Wands.jpg"
}

def get_wikimedia_url(title):
    """Получает URL изображения через API Викимедии."""
    try:
        api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{title}&prop=imageinfo&iiprop=url&format=json"
        response = requests.get(api_url, headers=HEADERS)
        data = response.json()
        
        pages = data['query']['pages']
        for page_id in pages:
            if 'imageinfo' in pages[page_id]:
                return pages[page_id]['imageinfo'][0]['url']
    except Exception as e:
        print(f"Ошибка при получении URL: {e}")
    return None

def download_card(card_name, filename, suit_code=None):
    """Скачивает карту Таро."""
    print(f"Пробуем скачать карту {card_name}...")
    
    # Проверяем, существует ли уже файл
    os.makedirs('images/tarot', exist_ok=True)
    filepath = os.path.join('images/tarot', f"{card_name}.jpg")
    if os.path.exists(filepath):
        print(f"Файл {card_name}.jpg уже существует, пропускаем...")
        return True
    
    # Проверяем, есть ли карта в списке особых случаев
    if card_name in SPECIAL_CARDS:
        special_filename = SPECIAL_CARDS[card_name]
        print(f"Используем специальное имя файла: {special_filename}")
        url = get_wikimedia_url(special_filename)
        if url:
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Успешно скачано: {card_name}")
                    return True
            except Exception as e:
                print(f"Ошибка при скачивании {card_name}: {e}")
            time.sleep(1)
    
    # Формируем список возможных имен файлов
    search_titles = []
    
    if suit_code:
        # Для Младших Арканов
        search_titles.extend([
            f"{suit_code}{filename}.jpg",  # Например: pents01.jpg
            f"{suit_code.capitalize()}{filename}.jpg",  # Например: Wands01.jpg
            f"RWS_{suit_code.capitalize()}_{filename}.jpg"  # Например: RWS_Wands_01.jpg
        ])
    else:
        # Для Старших Арканов
        search_titles.extend([
            f"RWS_Tarot_{filename}.jpg",  # Например: RWS_Tarot_00_Fool.jpg
            f"RWS_{filename}.jpg"  # Например: RWS_00_Fool.jpg
        ])
    
    for title in search_titles:
        print(f"Пробуем найти: {title}")
        url = get_wikimedia_url(title)
        if url:
            try:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Успешно скачано: {card_name}")
                    return True
            except Exception as e:
                print(f"Ошибка при скачивании {card_name}: {e}")
        time.sleep(1)
    
    print(f"Не удалось найти изображение для {card_name}")
    return False

def main():
    print("Начинаем скачивание всех карт Таро...")
    
    # Старшие Арканы
    major_arcana = [
        ("Fool", "00_Fool"),
        ("Magician", "01_Magician"),
        ("High_Priestess", "02_High_Priestess"),
        ("Empress", "03_Empress"),
        ("Emperor", "04_Emperor"),
        ("Hierophant", "05_Hierophant"),
        ("Lovers", "06_Lovers"),
        ("Chariot", "07_Chariot"),
        ("Strength", "08_Strength"),
        ("Hermit", "09_Hermit"),
        ("Wheel_of_Fortune", "10_Wheel_of_Fortune"),
        ("Justice", "11_Justice"),
        ("Hanged_Man", "12_Hanged_Man"),
        ("Death", "13_Death"),
        ("Temperance", "14_Temperance"),
        ("Devil", "15_Devil"),
        ("Tower", "16_Tower"),
        ("Star", "17_Star"),
        ("Moon", "18_Moon"),
        ("Sun", "19_Sun"),
        ("Judgement", "20_Judgement"),
        ("World", "21_World")
    ]
    
    print("\nСкачиваем Старшие Арканы...")
    for card_name, filename in major_arcana:
        download_card(card_name, filename)
        time.sleep(1)
    
    # Младшие Арканы
    suits = {
        "Wands": "wands",
        "Cups": "cups",
        "Swords": "swords",
        "Pentacles": "pents"
    }
    print("\nСкачиваем Младшие Арканы...")
    
    for suit_name, suit_code in suits.items():
        print(f"\nСкачиваем масть {suit_name}...")
        
        # Числовые карты (1-10)
        for i in range(1, 11):
            card_name = f"{NUMBER_NAMES[i]}_of_{suit_name}"
            filename = f"{i:02d}"  # 01, 02, ..., 10
            download_card(card_name, filename, suit_code)
            time.sleep(1)
        
        # Фигурные карты
        court_cards = ["Page", "Knight", "Queen", "King"]
        for i, court in enumerate(court_cards, 11):
            card_name = f"{court}_of_{suit_name}"
            filename = f"{i:02d}"  # 11, 12, 13, 14
            download_card(card_name, filename, suit_code)
            time.sleep(1)
    
    print("\nСкачивание завершено!")

if __name__ == "__main__":
    main() 