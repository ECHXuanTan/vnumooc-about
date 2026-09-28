#!/usr/bin/env python3
"""Build a timeline seed without presenting invented education as fact.

Entries with a university URL were transcribed from that person's profile and
remain pending review. Every other profile gets visibly illustrative slots with
no real years, institutions, or fields of study.
"""

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "instructors.json"
OUTPUT = ROOT / "data" / "instructors_education_seed.json"


def item(period, degree, field, institution):
    return {"period": period, "degree": degree, "field": field, "institution": institution}


HCMUS = "Trường Đại học Khoa học tự nhiên, ĐHQG-HCM"
SOURCE_TIMELINES = {
    "hcmus:mai-hoang-bien": {
        "source_url": "https://en.hcmus.edu.vn/profile/assoc-prof-mai-hoang-bien/",
        "items": [
            item("2004", "Cử nhân", "Toán và Tin học", HCMUS),
            item("2008", "Thạc sĩ", "Đại số và Lý thuyết số", HCMUS),
            item("2014", "Tiến sĩ", "Toán học", "Đại học Padua và Đại học Leiden"),
        ],
    },
    "hcmus:hoang-duc-huy": {
        "source_url": "https://en.hcmus.edu.vn/profile/assoc-prof-dr-hoang-duc-huy/",
        "items": [
            item("1998", "Cử nhân", "Sinh học", HCMUS),
            item("2002", "Thạc sĩ", "Sinh học môi trường", "Đại học Nữ Seoul, Hàn Quốc"),
            item("2005", "Tiến sĩ", "Sinh thái học và Sinh học tiến hóa", "Đại học Nữ Seoul, Hàn Quốc"),
        ],
    },
    "hcmus:do-thuong-kiet": {
        "source_url": "https://fbb.hcmus.edu.vn/do-thuong-kiet3.html",
        "items": [
            item("2001–2005", "Cử nhân", "Sinh học", HCMUS),
            item("2006–2009", "Thạc sĩ", "Sinh lý thực vật", HCMUS),
            item("2009–2014", "Tiến sĩ", "Sinh lý thực vật", HCMUS),
        ],
    },
    "hcmus:dang-hoai-trung": {
        "source_url": "https://phys.hcmus.edu.vn/vi/vat-ly-dia-cau/nhan-su/ts-dang-hoai-trung",
        "items": [
            item("2007", "Cử nhân", "", HCMUS),
            item("2012", "Thạc sĩ", "", HCMUS),
            item("2019", "Tiến sĩ", "", HCMUS),
        ],
    },
    "hcmus:le-thuy-thanh-giang": {
        "source_url": "https://phys.hcmus.edu.vn/vi/vat-ly-chat-ran/nhan-su/ts-le-thuy-thanh-giang",
        "items": [
            item("2008", "Thạc sĩ", "", HCMUS),
            item("2014", "Tiến sĩ", "", "Đại học Grenoble Alpes, Pháp"),
        ],
    },
    "hcmus:nguyen-ngoc-truong": {
        "source_url": "https://phys.hcmus.edu.vn/vi/vat-ly-dia-cau/nhan-su/ths-nguyen-ngoc-truong",
        "items": [
            item("2012", "Cử nhân", "", HCMUS),
            item("2015", "Thạc sĩ", "", HCMUS),
        ],
    },
}


def person_id(person):
    name = unicodedata.normalize("NFD", person["n"].replace("đ", "d").replace("Đ", "D"))
    name = "".join(char for char in name if unicodedata.category(char) != "Mn").lower()
    return f'{person["u"]}:{re.sub(r"[^a-z0-9]+", "-", name).strip("-")}'


def demo_items(title):
    # These are UI slots, not biographical assertions. The period is deliberately
    # non-numeric so it cannot be mistaken for a real graduation year.
    if title in ("GS.TS.", "PGS.TS.", "TS."):
        degrees = ("Cử nhân", "Thạc sĩ", "Tiến sĩ")
    elif title == "NCS.ThS.":
        degrees = ("Cử nhân", "Thạc sĩ", "Nghiên cứu sinh")
    elif title == "ThS.":
        degrees = ("Cử nhân", "Thạc sĩ")
    else:
        degrees = ("Học vấn",)
    return [item("20XX", f"Mốc {degree} minh họa", "Ngành học đang cập nhật",
                 "Cơ sở đào tạo đang cập nhật") for degree in degrees]


def main():
    people = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = {}
    for person in people:
        key = person_id(person)
        if key in result:
            raise ValueError(f"Duplicate person ID: {key}")
        if key in SOURCE_TIMELINES:
            result[key] = {"status": "source_candidate", **SOURCE_TIMELINES[key]}
        else:
            result[key] = {"status": "demo", "source_url": None,
                           "items": demo_items(person["t"])}
    unused = set(SOURCE_TIMELINES) - set(result)
    if unused:
        raise ValueError(f"Source timelines do not match the original roster: {sorted(unused)}")
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sourced = sum(record["status"] == "source_candidate" for record in result.values())
    print(f"Wrote {len(result)} education timeline seeds: {sourced} sourced, {len(result)-sourced} demo")


if __name__ == "__main__":
    main()
