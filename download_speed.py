#!/usr/bin/env python3
"""Измеряет скорость скачивания: делает 10 последовательных запросов к адресу."""

import argparse
import sys
import time
from http.client import HTTPException
from urllib.request import Request, urlopen

REQUESTS = 10
TIMEOUT = 30  # секунд тишины от сервера, а не лимит на весь запрос
MEGABYTE = 10**6
# Многие серверы и CDN отвечают 403 на стандартный User-Agent «Python-urllib».
HEADERS = {"User-Agent": "download-speed/1.0"}


def download(url: str) -> tuple[float, int]:
    """Скачивает ответ целиком и возвращает время запроса (с) и размер тела (байты)."""
    start = time.perf_counter()
    with urlopen(Request(url, headers=HEADERS), timeout=TIMEOUT) as response:
        # Именно read() без аргумента: чтение порциями молча принимает оборванный ответ.
        size = len(response.read())
    return time.perf_counter() - start, size


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="адрес ресурса, например тяжёлой картинки")
    url = parser.parse_args().url

    try:
        times, sizes = zip(*(download(url) for _ in range(REQUESTS)))
    except (OSError, HTTPException, ValueError) as error:
        sys.exit(f"Ошибка: {error}")
    except KeyboardInterrupt:
        sys.exit("\nПрервано")

    total_time, total_size = sum(times), sum(sizes)
    print(f"Среднее время запроса:  {total_time / REQUESTS:.3f} с")
    print(f"Объём скачанных данных: {total_size / MEGABYTE:.2f} МБ")
    print(f"Скорость скачивания:    {total_size / total_time / MEGABYTE:.2f} МБ/с")


if __name__ == "__main__":
    main()
