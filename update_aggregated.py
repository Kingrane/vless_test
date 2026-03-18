import base64
import random
from urllib.request import urlopen, Request
from urllib.parse import unquote

# --- НАСТРОЙКИ ---

# Ссылки
URL_WHITE_CHECKED = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"
URL_VLESS_LITE = "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"

# Лимиты
LIMIT_RU = 35
LIMIT_OTHER = 15
TOTAL_LIMIT = LIMIT_RU + LIMIT_OTHER

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return ""

def get_country(line: str) -> str:
    """
    Честно ищет страну в названии.
    Возвращает 'ru', 'de', или 'other'.
    """
    try:
        # Берем текст после решетки (#)
        if "#" not in line: return "other"
        remark = unquote(line.split("#")[-1]).lower()

        # Проверяем РФ
        # Ищем: russia, ru_, rf, или флаг 🇷🇺
        if "russia" in remark or "ru_" in remark or "rf" in remark or "🇷🇺" in remark:
            return "ru"

        # Проверяем Германию
        # Ищем: germany, de_, frankfurt, или флаг 🇩🇪
        if "germany" in remark or "de_" in remark or "frankfurt" in remark or "🇩🇪" in remark:
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
    print("=== Запуск Честного Сборщика v3 ===")

    # --- ШАГ 1: ЗАГРУЗКА ВСЕХ ИСТОЧНИКОВ ---
    
    # Загружаем первый источник (White Checked)
    text1 = fetch_text(URL_WHITE_CHECKED)
    lines1 = [l.strip() for l in text1.splitlines() if l.strip().startswith("vless://")]
    
    # Загружаем второй источник (Vless Lite)
    text2 = fetch_text(URL_VLESS_LITE)
    lines2 = [l.strip() for l in text2.splitlines() if l.strip().startswith("vless://")]

    # ==========================================
    # ФАЙЛ 1: best_ru_de.txt (СТРОГО WHITE CHECKED)
    # ==========================================
    print("\n[1] Сборка best_ru_de.txt (строго RU + DE из White Checked)")
    
    pool_ru = []
    pool_de = []

    # Разбираем только первый источник
    for line in lines1:
        country = get_country(line)
        if country == "ru":
            pool_ru.append(line)
        elif country == "de":
            pool_de.append(line)
    
    # Убираем дубликаты
    pool_ru = list(dict.fromkeys(pool_ru))
    pool_de = list(dict.fromkeys(pool_de))
    
    print(f"Найдено в White Checked: РФ={len(pool_ru)}, DE={len(pool_de)}")

    # Берем 30 РФ и 20 DE
    random.shuffle(pool_ru)
    random.shuffle(pool_de)
    
    final_best = []
    final_best.extend(pool_ru[:30])
    final_best.extend(pool_de[:20])
    random.shuffle(final_best)
    
    save_file("best_ru_de", final_best)
    print(f"Готово best_ru_de: {len(final_best)} серверов")

    # ==========================================
    # ФАЙЛ 2: aggregated.txt (МИКС ИЗ ВСЕХ)
    # ==========================================
    print("\n[2] Сборка aggregated.txt (35 РФ + 15 Мир из всех источников)")
    
    # Объединяем оба источника для большого списка
    all_lines = lines1 + lines2
    
    pool_ru_mix = []
    pool_other_mix = []

    for line in all_lines:
        country = get_country(line)
        if country == "ru":
            pool_ru_mix.append(line)
        else:
            # Сюда попадут и DE, и OTHER (для разнообразия)
            pool_other_mix.append(line)

    # Убираем дубликаты
    pool_ru_mix = list(dict.fromkeys(pool_ru_mix))
    pool_other_mix = list(dict.fromkeys(pool_other_mix))
    
    print(f"Найдено в Миксе: РФ={len(pool_ru_mix)}, Других={len(pool_other_mix)}")

    # Берем 35 РФ
    random.shuffle(pool_ru_mix)
    final_agg = pool_ru_mix[:LIMIT_RU]
    
    # Берем 15 Других
    random.shuffle(pool_other_mix)
    final_agg.extend(pool_other_mix[:LIMIT_OTHER])
    
    random.shuffle(final_agg)
    
    save_file("aggregated", final_agg)
    print(f"Готово aggregated: {len(final_agg)} серверов")

if __name__ == "__main__":
    main()
