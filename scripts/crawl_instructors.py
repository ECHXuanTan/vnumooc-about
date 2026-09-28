#!/usr/bin/env python3
"""Create reviewable instructor profile seed data from Google search results.

Google results are obtained through Serper. Only pages on the instructor's
university domain are read for biographical fields. Nothing is published here.
"""

import argparse
import json
import os
import re
import sys
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "instructors.json"
OUTPUT = ROOT / "data" / "instructors_seed.json"
PUBLISHED = ROOT / "data" / "instructors_profiles.json"
KEY_FILE = ROOT.parents[1] / "config" / "serper_api_key.json"
SEARCH_URL = "https://google.serper.dev/search"
DOMAINS = {
    "hcmut": ("hcmut.edu.vn",),
    "hcmus": ("hcmus.edu.vn",),
    "ussh": ("hcmussh.edu.vn",),
    "uit": ("uit.edu.vn",),
    "iu": ("hcmiu.edu.vn",),
    "uel": ("uel.edu.vn",),
    "agu": ("agu.edu.vn",),
}
LABELS = {
    "expertise": ("lĩnh vực nghiên cứu", "hướng nghiên cứu", "chuyên môn", "research interests", "research areas"),
    "education": ("học vấn", "quá trình đào tạo", "trình độ đào tạo", "education", "academic background"),
}
THREAD_LOCAL = threading.local()


def session():
    if not hasattr(THREAD_LOCAL, "http"):
        THREAD_LOCAL.http = requests.Session()
        THREAD_LOCAL.http.headers.update({"User-Agent": "VNUMOOC instructor profile research/1.0"})
    return THREAD_LOCAL.http


def fold(value):
    value = unicodedata.normalize("NFD", value.replace("đ", "d").replace("Đ", "D"))
    return re.sub(r"\s+", " ", "".join(c for c in value if unicodedata.category(c) != "Mn")).lower().strip()


def person_id(person):
    name = re.sub(r"[^a-z0-9]+", "-", fold(person["n"])).strip("-")
    return f'{person["u"]}:{name}'


def allowed_url(url, domains):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    try:
        port_ok = parsed.port in (None, 443)
    except ValueError:
        return False
    return (parsed.scheme == "https" and not parsed.username and not parsed.password
            and port_ok and any(host == domain or host.endswith("." + domain) for domain in domains))


def blank(person):
    return {
        "person_id": person_id(person), "name": person["n"], "unit": person["dv"],
        "photo": None, "bio": None, "expertise": [], "education": [], "links": {},
        "sources": {}, "candidate_urls": [], "review_status": "pending", "searched_at": None,
    }


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def google_search(query, api_key):
    response = session().post(
        SEARCH_URL, headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "gl": "vn", "hl": "vi", "num": 10}, timeout=25,
    )
    response.raise_for_status()
    return response.json().get("organic", [])


def load_api_key():
    """Environment wins; local config is outside the published website and Git ignored."""
    if os.environ.get("SERPER_API_KEY"):
        return os.environ["SERPER_API_KEY"].strip()
    if KEY_FILE.exists():
        return str(json.loads(KEY_FILE.read_text(encoding="utf-8")).get("api_key", "")).strip()
    return ""


def get_html(url, domains):
    for _ in range(4):
        if not allowed_url(url, domains):
            return None
        response = session().get(url, timeout=20, allow_redirects=False,
                               headers={"Accept": "text/html"}, stream=True)
        try:
            if response.is_redirect:
                url = urljoin(url, response.headers.get("Location", ""))
                continue
            if not response.ok or "text/html" not in response.headers.get("Content-Type", "").lower():
                return None
            content = response.raw.read(1_000_001, decode_content=True)
            if len(content) > 1_000_000:
                return None
            response._content = content
            return BeautifulSoup(response.text, "html.parser"), response.url
        finally:
            response.close()
    return None


def meta(soup, *keys):
    for key in keys:
        tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""


def jsonld_people(soup):
    people = []
    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            kind = value.get("@type", [])
            if kind == "Person" or (isinstance(kind, list) and "Person" in kind):
                people.append(value)
            if "@graph" in value:
                visit(value["@graph"])
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            visit(json.loads(tag.string or tag.get_text()))
        except (ValueError, TypeError):
            continue
    return people


def labeled_values(soup, labels):
    values = []
    labels = {fold(label) for label in labels}
    for tag in soup.select("strong, b, h2, h3, h4, dt"):
        if fold(tag.get_text(" ", strip=True)).rstrip(":") not in labels:
            continue
        sibling = tag.find_next_sibling()
        if sibling and sibling.name in ("ul", "ol"):
            items = [li.get_text(" ", strip=True) for li in sibling.find_all("li")]
            if items:
                values.append("; ".join(items))
    for row in soup.select("tr"):
        cells = row.find_all(["th", "td"], recursive=False)
        if len(cells) >= 2 and fold(cells[0].get_text(" ", strip=True)).rstrip(":") in labels:
            values.append(cells[1].get_text(" ", strip=True))
    lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
    for i, line in enumerate(lines):
        normalized = fold(line)
        for label in labels:
            if normalized == label or normalized == label + ":":
                if i + 1 < len(lines):
                    values.append(lines[i + 1])
            elif normalized.startswith(label + ":"):
                values.append(line.split(":", 1)[1].strip())
    return list(dict.fromkeys(v for v in values if 3 <= len(v) <= 350))[:3]


def pick_photo(soup, page_url, domains, name, ld_person):
    candidates = []
    image = ld_person.get("image") if ld_person else None
    if isinstance(image, dict):
        image = image.get("url")
    if isinstance(image, str):
        candidates.append(image)
    for img in soup.find_all("img", alt=True):
        if fold(name) in fold(img.get("alt", "")):
            candidates.append(img.get("src") or img.get("data-src"))
    if "profile-card" in (soup.get("class") or []):
        images = soup.find_all("img")
        if len(images) == 1:
            candidates.append(images[0].get("src") or images[0].get("data-src"))
    for candidate in candidates:
        if candidate:
            url = urljoin(page_url, candidate)
            filename = urlparse(url).path.rsplit("/", 1)[-1].lower()
            if any(word in filename for word in ("blank", "placeholder", "spacer")):
                continue
            if allowed_url(url, domains):
                return {"url": url, "source_url": page_url, "usage_status": "pending"}
    return None


def extract_profile(soup, page_url, person):
    domains = DOMAINS[person["u"]]
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        if tag.name != "script" or tag.get("type") != "application/ld+json":
            tag.decompose()
    page_text = fold(soup.get_text(" ", strip=True))
    if fold(person["n"]) not in page_text:
        return {}
    people = [p for p in jsonld_people(soup) if fold(person["n"]) in fold(str(p.get("name", "")))]
    ld_person = people[0] if people else {}
    scoped = None
    for card in soup.select(".profile-card, .faculty-card, .lecturer-card, article"):
        if any(fold(person["n"]) in fold(h.get_text(" ", strip=True))
               for h in card.select("h1, h2, h3, h4, strong, figcaption")):
            scoped = card
            break
    headings = soup.select("h1, h2, h3, title")
    if not scoped and not ld_person and not any(fold(person["n"]) in fold(h.get_text(" ", strip=True)) for h in headings):
        return {}
    if scoped:
        soup = scoped
    result = {}
    photo = pick_photo(soup, page_url, domains, person["n"], ld_person)
    if photo:
        result["photo"] = photo
    descriptions = [ld_person.get("description"), meta(soup, "description", "og:description")]
    for description in descriptions:
        if isinstance(description, str) and 45 <= len(description) <= 500 and fold(person["n"]) in fold(description):
            result["bio"] = description.strip()
            break
    if not result.get("bio") and scoped:
        for section in soup.select("section, p"):
            description = section.get_text(" ", strip=True)
            if fold(person["n"]) in fold(description) and 60 <= len(description) <= 600:
                result["bio"] = re.split(r"DS Bài báo:|Liên hệ:", description, maxsplit=1)[0].strip()
                break
    expertise = labeled_values(soup, LABELS["expertise"])
    if expertise:
        result["expertise"] = [part.strip(" .") for part in re.split(r"[,;•]", expertise[0])
                               if 3 <= len(part.strip()) <= 100][:5]
    education = labeled_values(soup, LABELS["education"])
    if education:
        result["education"] = education
    links = {"official": page_url}
    for anchor in soup.find_all("a", href=True):
        url = urljoin(page_url, anchor["href"])
        host = (urlparse(url).hostname or "").lower()
        if url.startswith("https://") and "orcid.org" == host:
            links.setdefault("orcid", url)
        if url.startswith("https://") and host == "scholar.google.com" and "/citations?" in url:
            links.setdefault("scholar", url)
    result["links"] = links
    return result


def enrich(person, api_key):
    domains = DOMAINS[person["u"]]
    result = blank(person)
    result["searched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    queries = [f'"{person["n"]}" "{person["dv"]}" giảng viên',
               f'"{person["n"]}" site:{domains[0]}']
    visited = set()
    for query in queries:
        for item in google_search(query, api_key):
            url = item.get("link", "")
            if not allowed_url(url, domains) or url in visited:
                continue
            visited.add(url)
            result["candidate_urls"].append(url)
            try:
                fetched = get_html(url, domains)
            except requests.RequestException:
                continue
            if not fetched:
                continue
            soup, page_url = fetched
            fields = extract_profile(soup, page_url, person)
            if not fields:
                continue
            for field in ("photo", "bio", "expertise", "education", "links"):
                if fields.get(field) and not result[field]:
                    result[field] = fields[field]
                    result["sources"][field] = page_url
            if len(result["sources"]) == 5:
                break
        if sum(bool(result[field]) for field in ("photo", "bio", "expertise", "education")) >= 2:
            break
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", action="store_true", help="Create empty seed records without searching")
    parser.add_argument("--limit", type=int, default=0, help="Maximum people to search (0 = all)")
    parser.add_argument("--name", help="Search only names containing this text")
    parser.add_argument("--refresh", action="store_true", help="Search pending records again")
    parser.add_argument("--publish", action="store_true", help="Export approved fields for the website")
    parser.add_argument("--publish-seed", action="store_true", help="Export all instructor candidates for a draft website")
    parser.add_argument("--workers", type=int, default=6, help="Parallel instructor lookups (default: 6)")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 12:
        parser.error("--workers must be between 1 and 12")
    people = json.loads(SOURCE.read_text(encoding="utf-8"))
    ids = [person_id(p) for p in people]
    if len(ids) != len(set(ids)):
        parser.error("Duplicate person IDs in original instructor data")
    old = {p["person_id"]: p for p in json.loads(OUTPUT.read_text(encoding="utf-8"))} if OUTPUT.exists() else {}
    seed = [old.get(person_id(p), blank(p)) for p in people]
    write_json(OUTPUT, seed)
    if args.publish or args.publish_seed:
        approved = {}
        for person, record in zip(people, seed):
            if args.publish and record.get("review_status") != "approved":
                continue
            photo = record.get("photo")
            photo_url = None
            if isinstance(photo, dict) and (photo.get("usage_status") == "approved" or args.publish_seed):
                photo_url = photo.get("local_url")
                if not photo_url and photo.get("usage_status") == "approved":
                    photo_url = photo.get("url")
            approved[record["person_id"]] = {
                "person_id": record["person_id"],
                **person,
                "photo": photo_url,
                "photo_status": photo.get("usage_status") if isinstance(photo, dict) else None,
                "bio": record.get("bio"),
                "expertise": record.get("expertise", []),
                "education": record.get("education", []),
                "links": record.get("links", {}),
                "sources": record.get("sources", {}),
                "review_status": record.get("review_status", "pending"),
            }
        write_json(PUBLISHED, approved)
        kind = "seed" if args.publish_seed else "approved"
        print(f"Published {len(approved)} {kind} profiles: {PUBLISHED}")
        return
    if args.init:
        print(f"Initialized {len(seed)} seed records: {OUTPUT}")
        return
    api_key = load_api_key()
    if not api_key:
        parser.error("Set SERPER_API_KEY or config/serper_api_key.json at the VNUMOOC root; use --init for blank seeds")
    targets = []
    for index, person in enumerate(people):
        record = seed[index]
        if record.get("review_status") == "approved":
            continue
        if args.name and fold(args.name) not in fold(person["n"]):
            continue
        if record.get("searched_at") and not args.refresh:
            continue
        if args.limit and len(targets) >= args.limit:
            break
        targets.append((index, person))
    count = errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(enrich, person, api_key): (index, person)
                   for index, person in targets}
        for future in as_completed(futures):
            index, person = futures[future]
            try:
                seed[index] = future.result()
            except Exception as exc:
                errors += 1
                print(f"Search failed for {person['n']}: {type(exc).__name__}", file=sys.stderr)
                continue
            write_json(OUTPUT, seed)
            count += 1
            print(f"{count}/{len(targets)}: {person['n']} ({len(seed[index]['sources'])} candidate fields)")
    print(f"Saved {len(seed)} records; searched {count}, failed {errors}: {OUTPUT}")


if __name__ == "__main__":
    main()
