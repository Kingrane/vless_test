import base64
import random
import re
from urllib.request import urlopen, Request
from urllib.parse import unquote

# --- НАСТРОЙКИ ---
# Источники расставлены по приоритету
SOURCES = [
    # 1. Самый качественный (белые списки,Checked). Дает ~58% живых.
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
    
    # 2. Лайт версия (zieng2). Дает ~8% живых.
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    
    # 3. API (для разнообразия)
    "https://nowmeow.pw/8ybBd3fdCAQ6Ew5H0d66Y1hMbh63GpKUtEXQClIu/whitelist?ru=20&other=10"
]

LIMIT_RU = 35       # Сколько хотим РФ серверов
LIMIT_OTHER = 15    # Сколько хотим иностранных
LIMIT_TOTAL = LIMIT_RU + LIMIT_OTHER

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def detect_country(line: str) -> str:
    """
    Пытается понять страну по комментарию в конце строки.
    Обычно формат: vless://...#Country Name или vless://...#🇷🇺 Country
    """
    try:
        # Берем часть после решетки
        if "#" not in line: return "unknown"
        remark = line.split("#")[-1]
        remark = unquote(remark).lower()

        # Список ключевых слов для РФ
        ru_keys = ["russia", "ru_", "rf", "москва", "moscow", "🇷🇺"]
        
        # Проверяем РФ
        for key in ru_keys:
            if key in remark:
                return "ru"
        
        # Если это точно не РФ, считаем "other"
        return "other"
    except:
        return "unknown"

def main():
    print("--- Запуск гео-агрегатора ---")
    
    # Разделяем потоки
    pool_ru = []
    pool_other = []
    
    # Скачиваем и сортируем
    for url in SOURCES:
        text = fetch_text(url)
        lines = [l.strip() for l in text.splitlines() if l.strip().startswith("vless://")]
        
        # Разделяем по странам
        for line in lines:
            country = detect_country(line)
            if country == "ru":
                pool_ru.append(line)
            else:
                pool_other.append(line)

    # Удаляем дубликаты внутри списков
    pool_ru = list(dict.fromkeys(pool_ru))
    pool_other = list(dict.fromkeys(pool_other))
    
    print(f"Найдено в базах: РФ={len(pool_ru)}, Других={len(pool_other)}")

    # --- ЛОГИКА ОТБОРА ---
    final_list = []

    # 1. Берем РФ. 
    # Перемешиваем, чтобы каждый раз были разные, но из качественного пула.
    random.shuffle(pool_ru)
    
    # Берем сколько просили (35)
    final_list.extend(pool_ru[:LIMIT_RU])
    
    # 2. Добираем иностранные (15)
    random.shuffle(pool_other)
    final_list.extend(pool_other[:LIMIT_OTHER])

    # Если РФ не хватило, добиваем иностранцами до 50
    if len(final_list) < LIMIT_TOTAL:
        needed = LIMIT_TOTAL - len(final_list)
        # Берем остатки из других, которых еще нет в списке
        leftovers = [x for x in pool_other if x not in final_list]
        final_list.extend(leftovers[:needed])

    # Финальная перемешка (чтобы не шли блоком РФ, потом блоком Мир)
    random.shuffle(final_list)

    # --- СОХРАНЕНИЕ ---
    plain_content = "\n".join(final_list)
    base64_content = base64.b64encode(plain_content.encode("utf-8")).decode("utf-8")

    with open("aggregated.txt", "w", encoding="utf-8") as f:
        f.write(plain_content)
    
    with open("aggregated_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_content)
        
    print(f"Готово! В подписке: {len(final_list)} серверов (из них РФ попытка: {LIMIT_RU})")

if __name__ == "__main__":
    main()
