import base64
import random
import os
from urllib.request import urlopen, Request
import urllib.error

# --- НАСТРОЙКИ ---
# Список источников. nowmeow настроен на приоритет РФ.
SOURCES = [
    # 1. Проверенный список (белые списки)
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
    
    # 2. Лайт версия zieng2 (там 109 рабочих из 1100, берем легкую версию, меньше мусора)
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    
    # 3. API nowmeow: запрашиваем 20 РФ и 10 Мира (всего 30).
    # Это даст нам стабильное ядро из РФ серверов.
    "https://nowmeow.pw/8ybBd3fdCAQ6Ew5H0d66Y1hMbh63GpKUtEXQClIu/whitelist?ru=20&other=10"
]

LIMIT_TOTAL = 50
# Ссылка на текущий файл в твоем репозитории (чтобы скачать старый список)
REPO_RAW_URL = "https://raw.githubusercontent.com/Kingrane/vless_agregator/main/aggregated.txt"

def fetch_text(url: str) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_vless_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("vless://"):
            lines.append(line)
    return lines

def main():
    print("--- Запуск умного агрегатора ---")
    
    # 1. Скачиваем старый список (если есть), чтобы сохранить рабочие сервера
    old_configs = []
    print("Попытка скачать предыдущий список...")
    old_text = fetch_text(REPO_RAW_URL)
    if old_text:
        old_configs = parse_vless_lines(old_text)
        print(f"Найдено старых конфигов: {len(old_configs)}")
    else:
        print("Предыдущий список пуст или не найден.")

    # 2. Скачиваем все свежие базы
    fresh_pool = []
    for url in SOURCES:
        print(f"Загрузка: {url.split('/')[2]} ...")
        text = fetch_text(url)
        if text:
            fresh_pool.extend(parse_vless_lines(text))
    
    # Удаляем дубликаты из свежего пула
    fresh_pool = list(dict.fromkeys(fresh_pool))
    print(f"Всего уникальных ключей в свежих базах: {len(fresh_pool)}")

    if not fresh_pool:
        print("Критическая ошибка: свежие базы пусты.")
        return

    # 3. Формируем новый список (Smart Merge)
    final_list = []
    
    # Логика "Старый друг лучше новых двух":
    # Если сервер был в старом списке И он до сих пор есть в свежих базах -> Берем его.
    # Это гарантирует, что мы не потеряем то, что уже работает.
    for config in old_configs:
        if config in fresh_pool:
            final_list.append(config)
    
    print(f"Сохранено из старого списка: {len(final_list)}")
    
    # 4. Если места еще много, добавляем рандом из свежих
    remaining_slots = LIMIT_TOTAL - len(final_list)
    if remaining_slots > 0:
        # Убираем из пула те, что мы уже взяли
        candidates = [x for x in fresh_pool if x not in final_list]
        
        # Перемешиваем кандидатов
        random.shuffle(candidates)
        
        # Берем сколько нужно
        new_additions = candidates[:remaining_slots]
        final_list.extend(new_additions)
        print(f"Добавлено новых рандомных: {len(new_additions)}")
    
    # Если старых было больше лимита (маловерноятно, но бывает), обрезаем
    final_list = final_list[:LIMIT_TOTAL]

    # 5. Сохраняем файлы
    plain_content = "\n".join(final_list)
    base64_content = base64.b64encode(plain_content.encode("utf-8")).decode("utf-8")

    with open("aggregated.txt", "w", encoding="utf-8") as f:
        f.write(plain_content)
    
    with open("aggregated_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_content)
        
    print(f"Готово! Итого в подписке: {len(final_list)} серверов.")

if __name__ == "__main__":
    main()
