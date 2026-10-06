#!/usr/bin/env python3
"""Build data/buildings.json for six Bangkok areas.

Phrom Phong stays the original Sukhumvit Soi 23–49 trial set. Ekamai, On Nut,
Silom–Sathorn, Asok–Nana, and Ari are every residential building whose center
is within 2.5 km of the BTS station, using OpenStreetMap only. Station
coordinates are the OpenStreetMap railway=station nodes. Buildings in more
than one area are stored once and list every area they fall in. Unnamed
buildings are included only when the address is specific enough to label them.
Data is © OpenStreetMap contributors, ODbL.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

BBOX = {"south": 13.720, "west": 100.558, "north": 13.745, "east": 100.582}
RADIUS_M = 2500
# Order is the order stored on each building and shown in the page header.
STATIONS = {
    "ekamai": {
        "id": "ekamai",
        "name": "Ekamai",
        "osm_name": "Ekkamai",
        "name_th": "เอกมัย",
        "ref": "E7",
        "osm_id": "node/5405616025",
        "lat": 13.7195385,
        "lng": 100.585111,
    },
    "on-nut": {
        "id": "on-nut",
        "name": "On Nut",
        "osm_name": "On Nut",
        "name_th": "อ่อนนุช",
        "ref": "E9",
        "osm_id": "node/5391620400",
        "lat": 13.7056249,
        "lng": 100.601004,
    },
    # BTS Sala Daeng, node/451697335 (S2). Interchange with MRT Si Lom.
    "silom-sathorn": {
        "id": "silom-sathorn",
        "name": "Silom–Sathorn",
        "osm_name": "Sala Daeng",
        "name_th": "ศาลาแดง",
        "ref": "S2",
        "osm_id": "node/451697335",
        "lat": 13.7285677,
        "lng": 100.5343416,
        "detail": "interchange with MRT Si Lom",
    },
    # BTS Asok, node/5391625873 (E4). Interchange with MRT Sukhumvit.
    "asok-nana": {
        "id": "asok-nana",
        "name": "Asok–Nana",
        "osm_name": "Asok",
        "name_th": "อโศก",
        "ref": "E4",
        "osm_id": "node/5391625873",
        "lat": 13.7370432,
        "lng": 100.5603571,
        "detail": "interchange with MRT Sukhumvit",
    },
    # BTS Ari, node/5388607091 (N5).
    "ari": {
        "id": "ari",
        "name": "Ari",
        "osm_name": "Ari",
        "name_th": "อารีย์",
        "ref": "N5",
        "osm_id": "node/5388607091",
        "lat": 13.7797077,
        "lng": 100.5446201,
    },
}
AREA_IDS = ["phrom-phong", *STATIONS]
UA = "thailand-rental-map/1.0 (Sukhumvit building directory; ODbL)"
# The public Overpass servers time out on a dense 2.5 km named-building query.
# Try the main instance, then the French mirror, then smaller tiles.
OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
)
SELECTOR_BASES = (
    'nwr["building"~"^(apartments|residential|condominium|house|dormitory|terrace|detached|bungalow)$"]',
    'nwr["building"]["name"]',
    'nwr["landuse"="residential"]["name"]',
)
RES_BUILDING = {
    "apartments",
    "residential",
    "condominium",
    "house",
    "dormitory",
    "terrace",
    "detached",
    "bungalow",
}
INCLUDE_RE = re.compile(
    r"condo|condominium|residence|residential|apartment|mansion|tower|place|"
    r"suite|court|heights|house|villa|home|คอนโด|ทาวเวอร์|แมนชั่น|เรสซิเดน|"
    r"อาคารชุด|บ้าน|สุขุมวิท",
    re.I,
)
EXCLUDE_RE = re.compile(
    r"hotel|hostel|resort|\binn\b|mall|hospital|clinic|school|university|"
    r"college|temple|mosque|church|station|market|\bspa\b|restaurant|cafe|"
    r"café|\bbar\b|\bbank\b|dispensary|cannabis|7-?eleven|\bbts\b|\bmrt\b|"
    r"\bwat\b|วัด|โรงแรม|ห้าง|ตลาด|สถานี|โรงเรียน|โรงพยาบาล|shopping|"
    r"supermarket|\boffice\b",
    re.I,
)
GENERIC_RE = re.compile(
    r"^(tower|building|block|อาคาร)\s*[a-z0-9]{1,3}$"
    r"|^(north|south|east|west)\s+tower$"
    r"|^อาคาร\s*\d+$",
    re.I,
)
THAI_RE = re.compile(r"[\u0e00-\u0e7f]")
LATIN_RE = re.compile(r"[A-Za-z]")
NAME_KEYS = ("name", "name:en", "name:th", "alt_name", "short_name", "official_name", "old_name")
AMENITY_SKIP = {
    "school",
    "university",
    "college",
    "hospital",
    "clinic",
    "place_of_worship",
    "fuel",
    "bank",
    "restaurant",
    "cafe",
    "fast_food",
    "bar",
    "marketplace",
}
EXTRA_ALIASES = {
    "way/340330015": [
        "D.S. Tower",
        "D.S. Tower 1",
        "D.S. Tower 1 Sukhumvit 33",
        "DS Tower 1",
        "DS Towers",
    ]
}


def overpass(query: str) -> list[dict]:
    last_error: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        host = endpoint.split("/")[2]
        try:
            req = urllib.request.Request(endpoint, data=query.encode(), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as response:
                elements = json.load(response)["elements"]
            print(f"    ok {host} {len(elements)}", flush=True)
            return elements
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            last_error = exc
            print(f"    fail {host}: {exc}", flush=True)
            time.sleep(2)
    raise RuntimeError(last_error)


def overpass_query(selector: str, timeout: int) -> str:
    return f"[out:json][timeout:{timeout}];\n{selector};\nout center tags;\n"


def quarter_boxes(south: float, west: float, north: float, east: float) -> list[tuple[float, float, float, float]]:
    mid_lat = (south + north) / 2
    mid_lng = (west + east) / 2
    return [
        (south, west, mid_lat, mid_lng),
        (south, mid_lng, mid_lat, east),
        (mid_lat, west, north, mid_lng),
        (mid_lat, mid_lng, north, east),
    ]


def fetch_bbox(base: str, south: float, west: float, north: float, east: float, depth: int = 0) -> list[dict]:
    selector = f"{base}({south:.7f},{west:.7f},{north:.7f},{east:.7f})"
    try:
        return overpass(overpass_query(selector, 80))
    except RuntimeError:
        if depth >= 3:
            raise
        print(f"    splitting bbox depth {depth + 1}", flush=True)
        got: list[dict] = []
        for box in quarter_boxes(south, west, north, east):
            got += fetch_bbox(base, *box, depth + 1)
        return got


def center_in_radius(element: dict, lat: float, lng: float) -> bool:
    point = center(element)
    return point is not None and haversine_m(point, (lat, lng)) <= RADIUS_M


def fetch_selector(base: str, lat: float, lng: float) -> list[dict]:
    """Same three Overpass filters as before. Fall back to tiles if the circle times out."""
    selector = f"{base}(around:{RADIUS_M},{lat},{lng})"
    try:
        return overpass(overpass_query(selector, 120))
    except RuntimeError:
        print("    circle timed out; fetching bbox tiles inside the same radius", flush=True)
        box = circle_bbox(lat, lng)
        got = fetch_bbox(base, box["south"], box["west"], box["north"], box["east"])
        return [element for element in got if center_in_radius(element, lat, lng)]


def fetch_elements(cache: Path | None = None) -> list[dict]:
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
    elements: list[dict] = []
    for station in STATIONS.values():
        cached = cache / f"osm-{station['id']}.json" if cache else None
        if cached and cached.exists():
            got = json.loads(cached.read_text())["elements"]
            print(f"cached {station['id']}: {len(got)} elements", flush=True)
            elements += got
            continue
        lat, lng = station["lat"], station["lng"]
        got: list[dict] = []
        print(f"fetch {station['id']} around {lat},{lng}", flush=True)
        for index, base in enumerate(SELECTOR_BASES):
            piece = cache / f"osm-{station['id']}-q{index}.json" if cache else None
            if piece and piece.exists():
                batch = json.loads(piece.read_text())["elements"]
                print(f"  cached {station['id']} query {index + 1}: {len(batch)}", flush=True)
            else:
                try:
                    batch = fetch_selector(base, lat, lng)
                except RuntimeError as exc:
                    raise SystemExit(f"Overpass failed for {station['id']} query {index + 1}: {exc}") from exc
                print(f"  {station['id']} query {index + 1}: {len(batch)}", flush=True)
                if piece:
                    piece.write_text(json.dumps({"elements": batch}))
            got += batch
        if cached:
            cached.write_text(json.dumps({"elements": got}))
        elements += got
    return elements


def center(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    point = element.get("center") or {}
    if "lat" in point and "lon" in point:
        return float(point["lat"]), float(point["lon"])
    return None


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(h))


def fold_name(value: str) -> str:
    chars = []
    for ch in value.lower():
        if ch.isalnum() or "\u0e00" <= ch <= "\u0e7f":
            chars.append(ch)
    return "".join(chars)


def split_names(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def deperiod(value: str) -> str:
    return re.sub(r"\.(?=\s|[A-Za-z]|$)", "", value).replace("  ", " ").strip()


def roman_digit(value: str) -> str:
    return re.sub(r"\bII\b", "2", re.sub(r"\bI\b", "1", value))


def has_name(tags: dict) -> bool:
    return any((tags.get(key) or "").strip() for key in NAME_KEYS)


def address_label(tags: dict) -> str | None:
    number = re.sub(r"\s+", " ", (tags.get("addr:housenumber") or "").strip())
    street = re.sub(r"\s+", " ", (tags.get("addr:street") or tags.get("addr:place") or "").strip())
    if number and street:
        label = street if number in street else f"{street} {number}"
    else:
        label = re.sub(r"\s+", " ", (tags.get("addr:full") or "").strip())
        if not re.search(r"\d", label):
            return None
    if len(label) < 4 or len(re.sub(r"[\d/\-]+", "", label).strip()) < 3:
        return None
    if EXCLUDE_RE.search(label) or GENERIC_RE.match(label):
        return None
    return label


def in_phrom_phong(lat: float, lng: float) -> bool:
    return BBOX["south"] <= lat <= BBOX["north"] and BBOX["west"] <= lng <= BBOX["east"]


def areas_for(lat: float, lng: float) -> list[str]:
    found = []
    if in_phrom_phong(lat, lng):
        found.append("phrom-phong")
    point = (lat, lng)
    for key, station in STATIONS.items():
        if haversine_m(point, (station["lat"], station["lng"])) <= RADIUS_M:
            found.append(key)
    return found


def building_type(tags: dict, name: str) -> str:
    blob = name.lower()
    kind = tags.get("building")
    apartmentish = bool(re.search(r"apartment|mansion|แมนชั่น", blob, re.I))
    condoish = bool(
        re.search(r"condo|condominium|residence|tower|place|suite|court|คอนโด|ทาวเวอร์|เรสซิเดน", blob, re.I)
    ) or kind in {"apartments", "condominium"}
    if apartmentish and not condoish:
        return "apartment"
    if condoish:
        return "condo"
    return "other"


def blocked(tags: dict) -> bool:
    blob = " ".join(
        tags.get(key) or ""
        for key in ("name", "name:en", "name:th", "alt_name", "tourism", "amenity", "shop", "office")
    )
    if EXCLUDE_RE.search(blob):
        return True
    if tags.get("tourism") in {"hotel", "hostel", "motel", "guest_house"}:
        return True
    if tags.get("amenity") in AMENITY_SKIP:
        return True
    return False


def keep(element: dict) -> bool:
    tags = element.get("tags") or {}
    if blocked(tags):
        return False
    name = (tags.get("name") or tags.get("name:en") or tags.get("name:th") or "").strip()
    if len(name) < 3 or GENERIC_RE.match(name):
        return False
    kind = tags.get("building")
    if kind in {"apartments", "condominium"}:
        return True
    if kind == "residential":
        if element["type"] == "node" and not INCLUDE_RE.search(name):
            return False
        return True
    if kind in RES_BUILDING and INCLUDE_RE.search(name):
        return True
    if tags.get("landuse") == "residential" and INCLUDE_RE.search(name):
        return True
    if kind == "yes" and INCLUDE_RE.search(name) and not tags.get("shop") and not tags.get("office"):
        return True
    return False


def include_element(element: dict) -> bool:
    tags = element.get("tags") or {}
    if has_name(tags):
        return keep(element)
    if blocked(tags):
        return False
    if tags.get("building") not in RES_BUILDING and tags.get("building") != "condominium":
        return False
    return address_label(tags) is not None


def score(element: dict) -> int:
    tags = element.get("tags") or {}
    kind = tags.get("building")
    value = 0
    if kind in {"apartments", "condominium"}:
        value += 5
    elif kind == "residential":
        value += 4
    elif tags.get("landuse") == "residential":
        value += 3
    elif kind == "yes":
        value += 2
    if element["type"] == "way":
        value += 2
    elif element["type"] == "relation":
        value += 3
    if tags.get("name:en"):
        value += 1
    if tags.get("name:th"):
        value += 1
    if has_name(tags):
        value += 2
    return value


def record(element: dict) -> dict:
    tags = element.get("tags") or {}
    lat, lng = center(element)
    raw_names = []
    for key in NAME_KEYS:
        raw_names.extend(split_names(tags.get(key)))
    label = address_label(tags)
    named = bool(raw_names)
    latin = [n for n in raw_names if LATIN_RE.search(n)]
    thai = [n for n in raw_names if THAI_RE.search(n)]
    name_en = tags.get("name:en") or next((n for n in latin if n), None)
    name_th = tags.get("name:th") or next((n for n in thai if n), None)
    display = name_en or tags.get("name") or name_th or label
    aliases: list[str] = []
    seen = {fold_name(display or "")}

    def add(alias: str | None) -> None:
        if not alias:
            return
        alias = alias.strip()
        folded = fold_name(alias)
        if len(folded) < 3 or folded in seen:
            return
        seen.add(folded)
        aliases.append(alias)

    for candidate in raw_names + [deperiod(n) for n in raw_names] + [roman_digit(n) for n in raw_names]:
        if candidate != display:
            add(candidate)
    if label and label != display:
        add(label)
    ref = f"{element['type']}/{element['id']}"
    existing = {alias.casefold() for alias in aliases}
    existing.add((display or "").casefold())
    for alias in EXTRA_ALIASES.get(ref, []):
        if alias.casefold() not in existing:
            aliases.append(alias)
            existing.add(alias.casefold())
    return {
        "id": f"osm-{element['type']}-{element['id']}",
        "name": display,
        "name_en": name_en,
        "name_th": name_th,
        "aliases": aliases,
        "type": building_type(tags, display or ""),
        "lat": round(lat, 7),
        "lng": round(lng, 7),
        "areas": areas_for(lat, lng),
        "named": named,
        "source": "openstreetmap",
        "osm_ref": ref,
    }


def circle_bbox(lat: float, lng: float) -> dict:
    dlat = RADIUS_M / 111320
    dlon = RADIUS_M / (111320 * math.cos(math.radians(lat)))
    return {"south": lat - dlat, "west": lng - dlon, "north": lat + dlat, "east": lng + dlon}


def union_bbox(boxes: list[dict]) -> dict:
    return {
        "south": min(box["south"] for box in boxes),
        "west": min(box["west"] for box in boxes),
        "north": max(box["north"] for box in boxes),
        "east": max(box["east"] for box in boxes),
    }


def skipped_unnamed(elements: list[dict]) -> dict[str, int]:
    """Unnamed residential buildings dropped for lack of a street + house number."""
    seen = set()
    counts = {key: 0 for key in AREA_IDS}
    counts["unique"] = 0
    for element in elements:
        point = center(element)
        if point is None:
            continue
        tags = element.get("tags") or {}
        kind = tags.get("building")
        if kind not in RES_BUILDING and kind != "condominium":
            continue
        if blocked(tags) or has_name(tags) or address_label(tags):
            continue
        areas = areas_for(*point)
        if not areas:
            continue
        key = (element["type"], element["id"])
        if key in seen:
            continue
        seen.add(key)
        counts["unique"] += 1
        for area in areas:
            if area in counts:
                counts[area] += 1
    return counts


def stamp_existing(building: dict) -> dict:
    """Keep a directory building and refresh which areas its center falls in."""
    areas = areas_for(building["lat"], building["lng"]) or list(building.get("areas") or ["phrom-phong"])
    return {
        "id": building["id"],
        "name": building["name"],
        "name_en": building.get("name_en"),
        "name_th": building.get("name_th"),
        "aliases": list(building.get("aliases") or []),
        "type": building["type"],
        "lat": building["lat"],
        "lng": building["lng"],
        "areas": areas,
        "named": bool(building.get("named", True)),
        "source": building.get("source") or "openstreetmap",
        "osm_ref": building.get("osm_ref") or "",
    }


def build(existing: list[dict], elements: list[dict]) -> dict:
    accepted: list[dict] = []
    seen_ids = set()
    seen_names: list[tuple[str, float, float]] = []

    def accept(item: dict) -> bool:
        if not item.get("areas"):
            return False
        if item["id"] in seen_ids:
            return False
        folded = fold_name(item["name"])
        for name, lat, lng in seen_names:
            if name == folded and haversine_m((lat, lng), (item["lat"], item["lng"])) < 80:
                return False
        seen_ids.add(item["id"])
        seen_names.append((folded, item["lat"], item["lng"]))
        accepted.append(item)
        return True

    for building in existing:
        accept(stamp_existing(building))

    unique = {}
    for element in elements:
        if center(element) is None:
            continue
        unique[(element["type"], element["id"])] = element
    ordered = sorted(unique.values(), key=score, reverse=True)
    for element in ordered:
        if not include_element(element):
            continue
        accept(record(element))

    accepted.sort(key=lambda item: (item["name"] or "").casefold())
    boxes = [BBOX, *[circle_bbox(station["lat"], station["lng"]) for station in STATIONS.values()]]
    return {
        "area": {
            "id": "bangkok",
            "name": "Phrom Phong, Ekamai, On Nut, Silom–Sathorn, Asok–Nana and Ari",
            "description": (
                "Phrom Phong along Sukhumvit Soi 23 to Soi 49, plus every residential "
                "building within 2.5 km of BTS Ekamai, BTS On Nut, BTS Sala Daeng "
                "(Silom–Sathorn), BTS Asok (Asok–Nana), and BTS Ari. A building in "
                "more than one area is stored once."
            ),
            "bbox": union_bbox(boxes),
        },
        "areas": [
            {
                "id": "phrom-phong",
                "name": "Phrom Phong",
                "kind": "bbox",
                "description": "Sukhumvit Soi 23 to Soi 49, around BTS Phrom Phong and the Asok and Thong Lo edges.",
                "bbox": BBOX,
            },
            *[
                {
                    "id": station["id"],
                    "name": station["name"],
                    "kind": "radius",
                    "radius_m": RADIUS_M,
                    "description": station_description(station),
                    "station": {
                        "name": station["osm_name"],
                        "name_th": station["name_th"],
                        "ref": station["ref"],
                        "osm_id": station["osm_id"],
                        "lat": station["lat"],
                        "lng": station["lng"],
                    },
                }
                for station in STATIONS.values()
            ],
        ],
        "attribution": (
            "© OpenStreetMap contributors. Building names and locations are from "
            "OpenStreetMap, available under the Open Database License (ODbL)."
        ),
        "retrieved_at": date.today().isoformat(),
        "buildings": accepted,
    }


def station_description(station: dict) -> str:
    text = f"Residential buildings within {RADIUS_M} m of BTS {station['osm_name']} ({station['ref']})"
    if station.get("detail"):
        text += f", {station['detail']}"
    return text + "."


def summarize(payload: dict, skipped: dict[str, int]) -> None:
    from collections import Counter

    buildings = payload["buildings"]
    print(f"unique {len(buildings)}")
    print("skipped unnamed", json.dumps(skipped, ensure_ascii=False))
    for area in AREA_IDS:
        rows = [b for b in buildings if area in b["areas"]]
        types = Counter(b["type"] for b in rows)
        named = sum(1 for b in rows if b["named"])
        address = sum(1 for b in rows if not b["named"])
        print(
            f"{area}: {len(rows)} named={named} address={address} "
            f"condo={types['condo']} apartment={types['apartment']} other={types['other']} "
            f"skipped_unnamed={skipped.get(area, 0)}"
        )
    pairs = (
        ("phrom-phong", "ekamai"),
        ("phrom-phong", "asok-nana"),
        ("phrom-phong", "silom-sathorn"),
        ("ekamai", "on-nut"),
        ("ekamai", "asok-nana"),
        ("silom-sathorn", "asok-nana"),
    )
    for left, right in pairs:
        count = sum(1 for b in buildings if left in b["areas"] and right in b["areas"])
        print(f"overlap {left}∩{right} {count}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", help="Directory of per-station Overpass JSON files. Missing stations are fetched and saved here.")
    parser.add_argument("--base", default="data/buildings.json", help="Existing directory to keep and dedupe against")
    parser.add_argument("-o", default="data/buildings.json")
    args = parser.parse_args()
    base_path = Path(args.base)
    # Read before the output is replaced. Keep every building already in the
    # directory (the Phrom Phong trial set and earlier station radii) and
    # refresh area membership. Overpass adds buildings for the station radii.
    existing = []
    if base_path.exists():
        existing = json.loads(base_path.read_text()).get("buildings") or []
    cache = Path(args.cache) if args.cache else None
    elements = fetch_elements(cache)
    payload = build(existing, elements)
    skipped = skipped_unnamed(elements)
    Path(args.o).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summarize(payload, skipped)
    print(f"wrote {args.o}")


if __name__ == "__main__":
    main()
