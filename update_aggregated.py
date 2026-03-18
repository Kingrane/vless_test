import base64
import random
from urllib.request import urlopen

SOURCES = [
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_lite.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-checked.txt",
    "https://nowmeow.pw/8ybBd3fdCAQ6Ew5H0d66Y1hMbh63GpKUtEXQClIu/whitelist?limit=50&ru=30&other=20",
]

LIMIT_TOTAL = 50  # сколько всего конфигов хотим на выходе


def fetch_text(url: str) -> str:
    with urlopen(url, timeout=15) as resp:
        # можно добавить обработку ошибок, retries и т.п.
        return resp.read().decode("utf-8", errors="ignore")


def parse_vless_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # if line.startswith("#"):  # можно оставить заголовки, если нужно
        #    continue
        if line.startswith("vless://"):
            lines.append(line)
        # trojan:// можно тоже забирать, если надо
        # elif line.startswith("trojan://"):
        #    lines.append(line)
    return lines


def main():
    all_vless = []
    for url in SOURCES:
        try:
            text = fetch_text(url)
            vless = parse_vless_lines(text)
            print(f"{url}: {len(vless)} vless lines")
            all_vless.extend(vless)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    if not all_vless:
        print("No vless configs found.")
        return

    # дедупликация
    unique = list(dict.fromkeys(all_vless))
    print(f"Total unique vless lines: {len(unique)}")

    # случайный выбор
    random.shuffle(unique)
    selected = unique[:LIMIT_TOTAL]

    # формируем выходные файлы
    plain_content = "\n".join(selected) + "\n"
    base64_content = base64.b64encode(plain_content.encode("utf-8")).decode("utf-8")

    with open("aggregated.txt", "w", encoding="utf-8") as f:
        f.write(plain_content)

    with open("aggregated_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_content)

    print("Saved aggregated.txt and aggregated_base64.txt")


if __name__ == "__main__":
    main()
