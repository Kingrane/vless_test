import base64
import random
from urllib.request import urlopen, Request
from urllib.parse import unquote

# --- ИСТОЧНИКИ ---
URL_WHITE = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"
URL_LITE = "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt"

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error: {e}")
        return ""

def get_type(line: str) -> str:
    """Определяет тип: RU, DE, ANYCAST, или OTHER."""
    try:
        if "#" not in line: return "OTHER"
        remark = unquote(line.split("#")[-1]).lower()
        
        # Сначала чекаем Anycast/VK (они приоритетнее)
        if "anycast" in remark or "vk" in remark or "yandex" in remark:
            return "ANYCAST"
        
        # Потом страны
        if "russia" in remark or "ru_" in remark or "rf" in remark or "🇷🇺" in remark:
            return "RU"
        if "germany" in remark or "de_" in remark or "frankfurt" in remark or "🇩🇪" in remark:
            return "DE"
            
        return "OTHER"
    except:
        return "OTHER"

def save_file(filename_base, content_list):
    plain = "\n".join(content_list)
    with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
        f.write(plain)
    with open(f"{filename_base}_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(plain.encode("utf-8")).decode("utf-8"))

def main():
    print("=== Запуск v5.0 (Четкая структура) ===")
    
    # 1. Загрузка
    text_white = fetch_text(URL_WHITE)
    lines_white = [l.strip() for l in text_white.splitlines() if l.strip().startswith("vless://")]
    
    text_lite = fetch_text(URL_LITE)
    lines_lite = [l.strip() for l in text_lite.splitlines() if l.strip().startswith("vless://")]

    # Разбиваем White Checked по категориям
    white_ru = []
    white_anycast = []
    white_de = []
    white_other = []
    
    for line in lines_white:
        t = get_type(line)
        if t == "RU": white_ru.append(line)
        elif t == "ANYCAST": white_anycast.append(line)
        elif t == "DE": white_de.append(line)
        else: white_other.append(line)

    # Разбиваем Lite по категориям (нам нужны только RU и OTHER)
    lite_ru = []
    lite_other = []
    
    for line in lines_lite:
        t = get_type(line)
        if t == "RU": lite_ru.append(line)
        else: lite_other.append(line) # DE и ANYCAST из Lite не берем в этот файл

    # ==========================================
    # ФАЙЛ 1: best_ru_de.txt (ЭЛИТА)
    # ==========================================
    print("\n[1] Сборка best_ru_de.txt")
    
    # 30 Russia
    random.shuffle(white_ru)
    selected = white_ru[:30]
    
    # 10 Anycast
    random.shuffle(white_anycast)
    selected += white_anycast[:10]
    
    # 10 Germany
    random.shuffle(white_de)
    selected += white_de[:10]
    
    # Перемешаем итог
    random.shuffle(selected)
    
    save_file("best_ru_de", selected)
    print(f"best_ru_de готово: {len(selected)} серверов")

    # ==========================================
    # ФАЙЛ 2: aggregated.txt (МИКС)
    # ==========================================
    print("\n[2] Сборка aggregated.txt")
    
    final_agg = []
    
    # 15 RU из White
    random.shuffle(white_ru)
    final_agg += white_ru[:15]
    
    # 15 RU из Lite
    random.shuffle(lite_ru)
    final_agg += lite_ru[:15]
    
    # 10 Random из White (любые, можно повторно, но лучше без дублей)
    # Берем вообще все оставшиеся white (ru+de+other)
    pool_white_all = lines_white
    random.shuffle(pool_white_all)
    # Берем те, которых еще нет в списке
    white_additions = [x for x in pool_white_all if x not in final_agg][:10]
    final_agg += white_additions
    
    # 10 Random из Lite (любые)
    random.shuffle(lines_lite)
    lite_additions = [x for x in lines_lite if x not in final_agg][:10]
    final_agg += lite_additions
    
    save_file("aggregated", final_agg)
    print(f"aggregated готово: {len(final_agg)} серверов")

if __name__ == "__main__":
    main()
