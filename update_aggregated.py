import base64
import random
import re
from urllib.request import urlopen, Request
from urllib.parse import unquote

# --- НАСТРОЙКИ ---
# Источники для ОСНОВНОЙ подписки (aggregated.txt)
SOURCES_MAIN = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://nowmeow.pw/8ybBd3fdCAQ6Ew5H0d66Y1hMbh63GpKUtEXQClIu/whitelist?ru=10&other=40"
]

# Источник для ЭЛИТНОЙ подписки (best_ru_de.txt)
SOURCE_ELITE = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"

LIMIT_RU = 30
LIMIT_DE = 20

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def detect_country(line: str) -> str:
    try:
        if "#" not in line: return "other"
        remark = line.split("#")[-1]
        remark = unquote(remark).lower()

        # РФ
        if "🇷🇺" in remark or "russia" in remark or "ru_" in remark or "rf" in remark:
            return "ru"
        
        # Германия
        if "🇩🇪" in remark or "germany" in remark or "de_" in remark or "frankfurt" in remark:
            return "de"
            
        return "other"
    except:
        return "other"

def process_sources(url_list):
    """Собирает все ключи из списка URL, сортирует по странам"""
    pool_ru = []
    pool_de = []
    pool_other = []
    
    for url in url_list:
        text = fetch_text(url)
        lines = [l.strip() for l in text.splitlines() if l.strip().startswith("vless://")]
        
        for line in lines:
            country = detect_country(line)
            if country == "ru":
                pool_ru.append(line)
            elif country == "de":
                pool_de.append(line)
            else:
                pool_other.append(line)
                
    # Дедупликация
    return list(dict.fromkeys(pool_ru)), list(dict.fromkeys(pool_de)), list(dict.fromkeys(pool_other))

def main():
    print("=== Запуск генератора подписок ===")
    
    # --- 1. ГЕНЕРАЦИЯ ОСНОВНОЙ ПОДПИСКИ (aggregated.txt) ---
    # Логика: 35 РФ + 15 Мир (как мы обсуждали ранее, но теперь ищем RU/DE глобально)
    print("\n[1/2] Генерация основной подписки...")
    ru_main, de_main, other_main = process_sources(SOURCES_MAIN)
    
    final_main = []
    random.shuffle(ru_main)
    final_main.extend(ru_main[:35]) # Берем 35 РФ
    
    # Добираем из Германии и прочих
    rest_pool = de_main + other_main
    random.shuffle(rest_pool)
    final_main.extend(rest_pool[:15]) # Берем 15 "Мир"
    
    random.shuffle(final_main)
    
    # Сохраняем основную
    with open("aggregated.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_main))
    with open("aggregated_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode("\n".join(final_main).encode("utf-8")).decode("utf-8"))
    print(f"Основная подписка готова: {len(final_main)} шт.")

    # --- 2. ГЕНЕРАЦИЯ ЭЛИТНОЙ ПОДПИСКИ (best_ru_de.txt) ---
    # Логика: Четко 30 РФ + 20 DE только из WHITE-CIDR-RU-checked
    print("\n[2/2] Генерация элитной подписки (RU+DE)...")
    ru_elite, de_elite, _ = process_sources([SOURCE_ELITE])
    
    print(f"Найдено в Elite источнике: РФ={len(ru_elite)}, DE={len(de_elite)}")
    
    final_elite = []
    
    # Берем 30 РФ
    random.shuffle(ru_elite)
    final_elite.extend(ru_elite[:LIMIT_RU])
    
    # Берем 20 DE
    random.shuffle(de_elite)
    final_elite.extend(de_elite[:LIMIT_DE])
    
    # Если РФ или DE не хватает, добирать ничего не будем (строгость)
    
    # Перемешаем, чтобы не шли подряд
    random.shuffle(final_elite)
    
    # Сохраняем элитную
    content_elite = "\n".join(final_elite)
    with open("best_ru_de.txt", "w", encoding="utf-8") as f:
        f.write(content_elite)
    with open("best_ru_de_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(content_elite.encode("utf-8")).decode("utf-8"))
        
    print(f"Элитная подписка готова: {len(final_elite)} шт.")
    print("\n=== Все готово! ===")

if __name__ == "__main__":
    main()
