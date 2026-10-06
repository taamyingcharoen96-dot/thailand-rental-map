#!/usr/bin/env python3
"""Build data/buildings.json for Phrom Phong, Ekamai, and On Nut.

Phrom Phong stays the original Sukhumvit Soi 23–49 trial set. Ekamai and On Nut
are every residential building whose center is within 2.5 km of the BTS station,
using OpenStreetMap only. Buildings in more than one area are stored once.
Unnamed buildings are included only when the address is specific enough to label
them. Data is © OpenStreetMap contributors, ODbL.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import urllib.request
from datetime import date
from pathlib import Path

BBOX = {"south": 13.720, "west": 100.558, "north": 13.745, "east": 100.582}
RADIUS_M = 2500
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
}
UA = "thailand-rental-map/1.0 (Sukhumvit building directory; ODbL)"
OVERPASS = "https://overpass-api.de/api/interpreter"
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
    req = urllib.request.Request(OVERPASS, data=query.encode(), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)["elements"]


def fetch_elements() -> list[dict]:
    elements: list[dict] = []
    for station in STATIONS.values():
        lat, lng = station["lat"], station["lng"]
        elements += overpass(
            f"""
            [out:json][timeout:120];
            nwr["building"~"^(apartments|residential|condominium|house|dormitory|terrace|detached|bungalow)$"](around:{RADIUS_M},{lat},{lng});
            out center tags;
            """
        )
        elements += overpass(
            f"""
            [out:json][timeout:90];
            nwr["building"]["name"](around:{RADIUS_M},{lat},{lng});
            out center tags;
            """
        )
        elements += overpass(
            f"""
            [out:json][timeout:50];
            nwr["landuse"="residential"]["name"](around:{RADIUS_M},{lat},{lng});
            out center tags;
            """
        )
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
    seen = set()
    counts = {key: 0 for key in ("phrom-phong", *STATIONS)}
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
        if not any(area in STATIONS for area in areas):
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


def load_cached(cache: Path) -> list[dict]:
    elements = []
    for path in sorted(cache.glob("osm-*.json")):
        elements += json.load(open(path))["elements"]
    if not elements:
        raise SystemExit(f"no Overpass cache in {cache}")
    return elements


def stamp_existing(building: dict) -> dict:
    building = dict(building)
    building["areas"] = areas_for(building["lat"], building["lng"]) or ["phrom-phong"]
    building["named"] = True
    building.setdefault("aliases", [])
    return building


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
            "id": "sukhumvit",
            "name": "Phrom Phong, Ekamai and On Nut",
            "description": (
                "Phrom Phong along Sukhumvit Soi 23 to Soi 49, plus every residential "
                "building within 2.5 km of BTS Ekamai and within 2.5 km of BTS On Nut."
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
                    "description": f"Residential buildings within {RADIUS_M} m of BTS {station['osm_name']} ({station['ref']}).",
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


def summarize(payload: dict, skipped: dict[str, int]) -> None:
    from collections import Counter

    print(f"buildings {len(payload['buildings'])}")
    print("skipped unnamed", json.dumps(skipped))
    for area in ("phrom-phong", "ekamai", "on-nut"):
        rows = [b for b in payload["buildings"] if area in b["areas"]]
        types = Counter(b["type"] for b in rows)
        named = sum(1 for b in rows if b["named"])
        address = sum(1 for b in rows if not b["named"])
        print(f"{area}: {len(rows)} named={named} address={address} types={dict(types)} skipped_unnamed={skipped.get(area, 0)}")
    both = sum(1 for b in payload["buildings"] if "ekamai" in b["areas"] and "phrom-phong" in b["areas"])
    circles = sum(1 for b in payload["buildings"] if "ekamai" in b["areas"] and "on-nut" in b["areas"])
    print(f"overlap phrom-phong∩ekamai {both}")
    print(f"overlap ekamai∩on-nut {circles}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", help="Directory of cached Overpass JSON files")
    parser.add_argument("--base", default="data/buildings.json", help="Existing directory to keep and dedupe against")
    parser.add_argument("-o", default="data/buildings.json")
    args = parser.parse_args()
    base_path = Path(args.base)
    existing = []
    if base_path.exists() and args.base == args.o:
        # Read before the output file is replaced. A rebuilt file is not a Phrom Phong base.
        current = json.loads(base_path.read_text())
        if current.get("area", {}).get("id") == "phrom-phong":
            existing = current["buildings"]
    elif base_path.exists():
        current = json.loads(base_path.read_text())
        existing = current["buildings"] if current.get("area", {}).get("id") == "phrom-phong" else []
    elements = load_cached(Path(args.cache)) if args.cache else fetch_elements()
    payload = build(existing, elements)
    skipped = skipped_unnamed(elements)
    Path(args.o).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summarize(payload, skipped)
    print(f"wrote {args.o}")


if __name__ == "__main__":
    main()
