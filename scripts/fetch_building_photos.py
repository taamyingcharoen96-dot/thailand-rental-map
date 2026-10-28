#!/usr/bin/env python3
"""Save public Google Maps place photos for named buildings in one area.

The default area is 1 km around The EmQuartier in Phrom Phong
(13.731225, 100.569476). Only named buildings are searched. Unnamed
footprints are skipped. Pass --lat, --lng, and --radius-m to point the
same script at another center later.

Each search uses the public Maps results (no Google login). A photo is
kept only when the place Google returns is near that building and the
image is a place photo rather than a map chip, logo, or profile picture.
Failures stay as a missing photo so the hover card can show "No photo".
"""

from __future__ import annotations

import argparse
import html
import io
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

EMQUARTIER_LAT = 13.731225
EMQUARTIER_LNG = 100.569476
DEFAULT_RADIUS_M = 1000
MATCH_M = 250
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
FID_RE = re.compile(r"0x[0-9a-f]+:0x[0-9a-f]+")
SIZE_RE = re.compile(r"=w(\d+)-h(\d+)")
BAD_CATEGORY = re.compile(
    r"restaurant|cafe|coffee|\bbar\b|hotel|hostel|mall|school|hospital|"
    r"clinic|\bbank\b|\bshop\b|\bstore\b|\bspa\b",
    re.I,
)


class Blocked(RuntimeError):
    pass


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(h))


def fold_name(value: str) -> str:
    return re.sub(r"[^a-z0-9\u0e00-\u0e7f]", "", value.lower())


def names_match(wanted: str, found: str) -> bool:
    left, right = fold_name(wanted), fold_name(found)
    if len(left) < 3 or len(right) < 3:
        return False
    return left in right or right in left


def opener():
    return urllib.request.build_opener()


def fetch(opener, url: str, timeout: int = 30) -> tuple[str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with opener.open(req, timeout=timeout) as response:
            body = response.read()
            status = getattr(response, "status", 200)
    except urllib.error.HTTPError as exc:
        if exc.code in {429, 503}:
            raise Blocked(f"HTTP {exc.code}") from exc
        raise
    if status in {429, 503}:
        raise Blocked(f"HTTP {status}")
    text_sample = body[:4000].decode("utf-8", "replace").lower()
    if "unusual traffic" in text_sample or "/sorry/" in text_sample:
        raise Blocked("unusual traffic")
    return url, body


def loads_maps(body: bytes):
    text = body.decode("utf-8", "replace")
    start = text.find("[")
    if start < 0:
        raise ValueError("no JSON")
    raw = text[start:]
    if raw.startswith(")]}'"):
        raw = raw.split("\n", 1)[-1] if "\n" in raw[:8] else raw[4:]
    return json.loads(raw)


def places_in(data) -> list[dict]:
    found: list[dict] = []

    def walk(node) -> None:
        if not isinstance(node, list):
            return
        for index, item in enumerate(node):
            if isinstance(item, str) and FID_RE.fullmatch(item) and not item.startswith("0x0:"):
                prev = node[index - 1] if index else None
                name = node[index + 1] if index + 1 < len(node) and isinstance(node[index + 1], str) else ""
                category = ""
                if index + 3 < len(node) and isinstance(node[index + 3], list):
                    head = node[index + 3][0] if node[index + 3] else None
                    if isinstance(head, str):
                        category = head
                lat = lng = None
                if (
                    isinstance(prev, list)
                    and len(prev) >= 2
                    and isinstance(prev[-1], (int, float))
                    and isinstance(prev[-2], (int, float))
                ):
                    lat, lng = float(prev[-2]), float(prev[-1])
                if lat is not None and 5 < lat < 21 and 90 < lng < 110 and name:
                    found.append({
                        "fid": item,
                        "name": name,
                        "category": category,
                        "lat": lat,
                        "lng": lng,
                    })
            elif isinstance(item, list):
                walk(item)

    walk(data)
    unique = []
    seen = set()
    for place in found:
        if place["fid"] in seen:
            continue
        seen.add(place["fid"])
        unique.append(place)
    return unique


def search_queries(building: dict) -> list[str]:
    name = building["name"]
    queries = [
        f"{name} Bangkok",
        f"{name} Phrom Phong Bangkok",
        f"{name} condominium Bangkok",
    ]
    if re.search(r"\bTowers\b", name) and not re.search(r"\d", name):
        queries.append(name.replace("Towers", "Towers 1") + " Bangkok")
        queries.append(name.replace("Towers", "Tower") + " Sukhumvit Bangkok")
    street = building.get("address")
    if street:
        queries.append(f"{name} {street} Bangkok")
    seen = set()
    ordered = []
    for query in queries:
        key = fold_name(query)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(query)
    return ordered[:5]


def acceptable(building: dict, place: dict) -> float | None:
    distance = haversine_m((building["lat"], building["lng"]), (place["lat"], place["lng"]))
    if distance > MATCH_M:
        return None
    if not names_match(building["name"], place["name"]):
        return None
    if BAD_CATEGORY.search(place.get("category") or ""):
        return None
    return distance


def find_place(opener, building: dict) -> dict | None:
    best = None
    best_distance = None
    for query in search_queries(building):
        url = "https://www.google.com/search?" + urllib.parse.urlencode({
            "hl": "en",
            "gl": "th",
            "tbm": "map",
            "q": query,
        })
        _, body = fetch(opener, url)
        try:
            data = loads_maps(body)
        except (json.JSONDecodeError, ValueError):
            continue
        for place in places_in(data):
            distance = acceptable(building, place)
            if distance is None:
                continue
            if best_distance is None or distance < best_distance:
                best = place
                best_distance = distance
        if best_distance is not None and best_distance <= 120:
            break
        time.sleep(0.25)
    if best is not None:
        best["distance_m"] = round(best_distance, 1)
    return best


def preview_pb(opener, place: dict) -> str:
    label = place["name"]
    slug = urllib.parse.quote(label, safe="")
    fid = place["fid"]
    url = (
        "https://www.google.com/maps/preview/place/"
        f"{slug}/@{place['lat']},{place['lng']},3876a,13.1y/data=!4m2!3m1!1s{fid}"
    )
    _, body = fetch(opener, url)
    text = body.decode("utf-8", "replace")
    match = re.search(r'href="(/maps/preview/place\?[^"]+)"', text)
    if not match:
        raise ValueError("no preview link")
    href = html.unescape(match.group(1))
    parsed = urllib.parse.urlparse("https://www.google.com" + href)
    pb = urllib.parse.parse_qs(parsed.query).get("pb", [""])[0]
    if not pb:
        raise ValueError("empty pb")
    return pb


def photo_candidates(data) -> list[str]:
    raw_urls: list[str] = []

    def walk(node) -> None:
        if isinstance(node, str):
            if "googleusercontent.com" in node or "ggpht.com" in node:
                raw_urls.append(node)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    ordered = []
    seen = set()
    for url in raw_urls:
        if url.startswith("//"):
            url = "https:" + url
        if not url.startswith("https://"):
            continue
        if "/a-/" in url or "/a/" in url or "AAAAAAAAAAI" in url:
            continue
        base = url.split("=")[0]
        if base in seen:
            continue
        seen.add(base)
        sized = SIZE_RE.search(url)
        if sized and (int(sized.group(1)) < 200 or int(sized.group(2)) < 150):
            continue
        ordered.append(base + "=w960-h640-k-no")
    return ordered


def place_photos(opener, place: dict) -> list[str]:
    pb = preview_pb(opener, place)
    url = "https://www.google.com/maps/preview/place?" + urllib.parse.urlencode({
        "authuser": "0",
        "hl": "en",
        "gl": "th",
        "q": place["name"],
        "pb": pb,
    })
    _, body = fetch(opener, url)
    return photo_candidates(loads_maps(body))


def write_jpeg(data: bytes, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        if not data.startswith(b"\xff\xd8\xff"):
            raise ValueError("not a jpeg and Pillow is not installed")
        dest.write_bytes(data)
        return
    image = Image.open(io.BytesIO(data))
    image = image.convert("RGB")
    image.thumbnail((960, 640))
    image.save(dest, "JPEG", quality=82, optimize=True)


def download_first(opener, urls: list[str], dest: Path) -> str:
    last_error = "no photo url"
    for url in urls[:4]:
        try:
            _, body = fetch(opener, url)
        except Blocked:
            raise
        except Exception as exc:  # noqa: BLE001 — try the next candidate
            last_error = str(exc)
            continue
        if len(body) < 8000:
            last_error = "tiny image"
            continue
        try:
            write_jpeg(body, dest)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            continue
        if dest.stat().st_size < 8000:
            dest.unlink(missing_ok=True)
            last_error = "tiny image"
            continue
        return url
    raise ValueError(last_error)


def sample_buildings(payload: dict, lat: float, lng: float, radius_m: float, only: set[str]) -> list[dict]:
    chosen = []
    for building in payload.get("buildings") or []:
        if not building.get("named"):
            continue
        if only and building["id"] not in only:
            continue
        distance = haversine_m((lat, lng), (building["lat"], building["lng"]))
        if distance <= radius_m:
            chosen.append(building)
    chosen.sort(key=lambda building: haversine_m((lat, lng), (building["lat"], building["lng"])))
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--buildings", default="data/buildings.json")
    parser.add_argument("--lat", type=float, default=EMQUARTIER_LAT)
    parser.add_argument("--lng", type=float, default=EMQUARTIER_LNG)
    parser.add_argument("--radius-m", type=float, default=DEFAULT_RADIUS_M)
    parser.add_argument("--only", default="", help="Comma-separated building ids")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--report", default="data/building-photo-report.json")
    args = parser.parse_args()

    path = Path(args.buildings)
    payload = json.loads(path.read_text(encoding="utf-8"))
    only = {item.strip() for item in args.only.split(",") if item.strip()}
    buildings = sample_buildings(payload, args.lat, args.lng, args.radius_m, only)
    if args.limit:
        buildings = buildings[: args.limit]
    photo_dir = Path("photos/buildings")
    photo_dir.mkdir(parents=True, exist_ok=True)
    client = opener()
    report = {
        "center": {"lat": args.lat, "lng": args.lng, "radius_m": args.radius_m},
        "named_in_radius": len(sample_buildings(payload, args.lat, args.lng, args.radius_m, set())),
        "attempted": len(buildings),
        "saved": [],
        "skipped": [],
        "note": (
            "Public Google Maps place photos for named buildings near this center. "
            "No login. A skip means Maps had no nearby place or no usable photo; "
            "the hover card shows No photo."
        ),
    }
    blocked_streak = 0
    for index, building in enumerate(buildings, start=1):
        dest = photo_dir / f"{building['id']}.jpg"
        rel = f"photos/buildings/{building['id']}.jpg"
        if dest.exists() and not args.force and dest.stat().st_size > 8000:
            building["photo_url"] = rel
            report["saved"].append({"id": building["id"], "name": building["name"], "reused": True})
            print(f"{index}/{len(buildings)} reuse {building['name']}", flush=True)
            continue
        print(f"{index}/{len(buildings)} {building['name']}", flush=True)
        try:
            place = find_place(client, building)
            if not place:
                building.pop("photo_url", None)
                report["skipped"].append({
                    "id": building["id"],
                    "name": building["name"],
                    "reason": "no nearby Google place",
                })
                print("  no nearby place", flush=True)
                blocked_streak = 0
                time.sleep(0.3)
                continue
            urls = place_photos(client, place)
            source = download_first(client, urls, dest)
            building["photo_url"] = rel
            report["saved"].append({
                "id": building["id"],
                "name": building["name"],
                "place": place["name"],
                "distance_m": place["distance_m"],
                "source": source,
            })
            print(f"  saved {place['name']} ({place['distance_m']} m)", flush=True)
            blocked_streak = 0
        except Blocked as exc:
            blocked_streak += 1
            report["skipped"].append({
                "id": building["id"],
                "name": building["name"],
                "reason": f"blocked: {exc}",
            })
            print(f"  blocked {exc}", flush=True)
            if blocked_streak >= 3:
                print("stopping after repeated blocks", flush=True)
                break
            time.sleep(8 * blocked_streak)
            continue
        except Exception as exc:  # noqa: BLE001 — record and continue
            building.pop("photo_url", None)
            if dest.exists() and dest.stat().st_size < 8000:
                dest.unlink(missing_ok=True)
            report["skipped"].append({
                "id": building["id"],
                "name": building["name"],
                "reason": str(exc),
            })
            print(f"  skip {exc}", flush=True)
            blocked_streak = 0
        time.sleep(0.45)
        if index % 15 == 0:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"saved {len(report['saved'])} skipped {len(report['skipped'])} wrote {path}",
        flush=True,
    )


if __name__ == "__main__":
    main()
