import base64
import random
from urllib.request import urlopen, Request
from urllib.parse import unquote

# --- НАСТРОЙКИ ---

# 1. Источники
URL_ELITE = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"
URL_COMMON = "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"

# 2. Лимиты для Elite файла (best_ru_de.txt)
LIMIT_VK_ANYCAST = 10  # Сколько берем "самых живых" (VK/Anycast)
LIMIT_RU_SIMPLE = 25   # Сколько берем обычной России
LIMIT_DE = 15          # Сколько берем Германии
TOTAL_ELITE_LIMIT = LIMIT_VK_ANYCAST + LIMIT_RU_SIMPLE + LIMIT_DE

# Лимит для Common файла (aggregated.txt)
LIMIT_COMMON = 50

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def get_score(line: str) -> int:
    """Оценка качества: VK/Anycast получают +100 очков."""
    try:
        remark = unquote(line.split("#")[-1]).lower()
        if any(x in remark for x in ["vk", "yandex", "anycast"]):
            return 100
        return 0
    except:
        return -100

def detect_country(line: str) -> str:
    """Определяет страну по флагу или тексту."""
    try:
        if "#" not in line: return "other"
        remark = unquote(line.split("#")[-1]).lower()
        
        # РФ
        if "🇷🇺" in remark or "russia" in remark or "ru_" in remark or "rf" in remark:
            return "ru"
        
        # Германия
        if "🇩🇪" in remark or "germany" in remark or "de_" in remark or "frankfurt" in remark:
            return "de"
            
        return "other"
    except:
        return "other"

def save_file(filename_base, content_list):
    plain = "\n".join(content_list)
    with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
        f.write(plain)
    with open(f"{filename_base}_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(plain.encode("utf-8")).decode("utf-8"))

def main():
    print("=== Запуск Аккуратного Сборщика ===")
    
    # ==========================================
    # ФАЙЛ 1: best_ru_de.txt (ЭЛИТА)
    # ==========================================
    print("\n[1] Генерация best_ru_de.txt (Элита)")
    text_elite = fetch_text(URL_ELITE)
    lines_elite = [l.strip() for l in text_elite.splitlines() if l.strip().startswith("vless://")]

    # Классификация
    pool_vk_anycast = []
    pool_ru_simple = []
    pool_de = []

    for line in lines_elite:
        country = detect_country(line)
        score = get_score(line)
        
        # Сначала разбираем элиту (VK/Anycast), считаем их РФ
        if score == 100:
            pool_vk_anycast.append(line)
        elif country == "ru":
            pool_ru_simple.append(line)
        elif country == "de":
            pool_de.append(line)

    # Сортировка и отбор
    # VK/Anycast сортируем по принципу "как есть", просто берем сколько нужно
    # Если их меньше лимита - возьмем всех
    random.shuffle(pool_vk_anycast)
    selected_vk = pool_vk_anycast[:LIMIT_VK_ANYCAST]

    # Обычная РФ
    random.shuffle(pool_ru_simple)
    selected_ru = pool_ru_simple[:LIMIT_RU_SIMPLE]

    # Германия
    random.shuffle(pool_de)
    selected_de = pool_de[:LIMIT_DE]

    # Сборка итога
    final_elite = selected_vk + selected_ru + selected_de
    
    # Если VK/Anycast было мало, добираем обычной РФ
    if len(selected_vk) < LIMIT_VK_ANYCAST:
        shortage = LIMIT_VK_ANYCAST - len(selected_vk)
        # Берем дополнительно из pool_ru_simple, но те, которых еще нет в списке
        extras = [x for x in pool_ru_simple if x not in final_elite][:shortage]
        final_elite.extend(extras)

    # Если DE мало, добирать не будем (строгость)
    
    random.shuffle(final_elite)
    
    # Если всего набралось меньше лимита (например, DE нет), предупреждаем
    if len(final_elite) < TOTAL_ELITE_LIMIT:
        print(f"Внимание! Набрано меньше лимита: {len(final_elite)} из {TOTAL_ELITE_LIMIT}")

    save_file("best_ru_de", final_elite)
    print(f"Готово: VK/Any:{len(selected_vk)}, RU:{len(selected_ru)}, DE:{len(selected_de)} | Всего: {len(final_elite)}")

    # ==========================================
    # ФАЙЛ 2: aggregated.txt (МАССОВКА)
    # ==========================================
    print("\n[2] Генерация aggregated.txt (Массовка)")
    text_common = fetch_text(URL_COMMON)
    lines_common = [l.strip() for l in text_common.splitlines() if l.strip().startswith("vless://")]
    
    # Просто мешаем и берем 50 штук
    random.shuffle(lines_common)
    final_common = lines_common[:LIMIT_COMMON]
    
    save_file("aggregated", final_common)
    print(f"Готово: {len(final_common)} серверов из vless_lite.")

if __name__ == "__main__":
    main()
