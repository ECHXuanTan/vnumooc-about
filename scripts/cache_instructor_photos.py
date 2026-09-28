#!/usr/bin/env python3
"""Cache candidate university portraits for the local seed website."""

import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import requests
from PIL import Image

from crawl_instructors import DOMAINS, OUTPUT, ROOT, allowed_url, write_json


ASSETS = ROOT / "assets" / "about" / "instructors"
MAX_BYTES = 8_000_000
EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def download(record):
    photo = record.get("photo")
    if not isinstance(photo, dict) or photo.get("local_url"):
        return None
    url = photo.get("url", "")
    domains = DOMAINS[record["person_id"].split(":", 1)[0]]
    for _ in range(4):
        if not allowed_url(url, domains):
            return None
        try:
            response = requests.get(url, timeout=(5, 20), stream=True, allow_redirects=False,
                                    headers={"User-Agent": "Mozilla/5.0 (VNUMOOC profile seed)"})
        except requests.RequestException:
            return None
        with response:
            if response.is_redirect:
                url = urljoin(url, response.headers.get("Location", ""))
                continue
            if not response.ok or not response.headers.get("Content-Type", "").lower().startswith("image/"):
                return None
            chunks, size = [], 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > MAX_BYTES:
                    return None
                chunks.append(chunk)
            content = b"".join(chunks)
            try:
                image = Image.open(io.BytesIO(content))
                fmt, width, height = image.format, *image.size
                image.verify()
            except (OSError, ValueError):
                return None
            if fmt not in EXTENSIONS or min(width, height) < 128 or not 0.4 <= width / height <= 3:
                return None
            filename = record["person_id"].replace(":", "-") + EXTENSIONS[fmt]
            path = ASSETS / filename
            ASSETS.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return record["person_id"], "assets/about/instructors/" + filename
    return None


def main():
    records = json.loads(OUTPUT.read_text(encoding="utf-8"))
    targets = [record for record in records if isinstance(record.get("photo"), dict)
               and not record["photo"].get("local_url")]
    cached = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        for future in as_completed([pool.submit(download, record) for record in targets]):
            result = future.result()
            if not result:
                continue
            person_id, local_url = result
            record = next(item for item in records if item["person_id"] == person_id)
            record["photo"]["local_url"] = local_url
            write_json(OUTPUT, records)
            cached += 1
            print(f"Cached {cached}/{len(targets)}: {record['name']}", flush=True)
    print(f"Cached {cached} portraits; {len(targets) - cached} unavailable")


if __name__ == "__main__":
    main()
