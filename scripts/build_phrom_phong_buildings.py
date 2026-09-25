#!/usr/bin/env python3
"""Build data/buildings.json for the Phrom Phong trial area from OpenStreetMap.

The bbox covers Sukhumvit Soi 23 through Soi 49, including the blocks around
BTS Phrom Phong and the Asok and Thong Lo edges. Only named residential
buildings and residential complexes are kept. Data is © OpenStreetMap
contributors, ODbL.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import urllib.request
from datetime import date

BBOX = {"south": 13.720, "west": 100.558, "north": 13.745, "east": 100.582}
UA = "thailand-rental-map/1.0 (Phrom Phong building directory; ODbL)"
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
# Listing-specific aliases for the complex OSM names only as "D.S. Towers".
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
    req = urllib.request.Request(
        OVERPASS, data=query.encode(), headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)["elements"]


def fetch_elements() -> list[dict]:
    south, west, north, east = (
        BBOX["south"],
        BBOX["west"],
        BBOX["north"],
        BBOX["east"],
    )
    buildings = overpass(
        f"""
        [out:json][timeout:60];
        nwr["building"]["name"]({south},{west},{north},{east});
        out center tags;
        """
    )
    landuse = overpass(
        f"""
        [out:json][timeout:40];
        nwr["landuse"="residential"]["name"~"Tower|Condo|Residence|Apartment|Mansion|คอนโด|ทาวเวอร์",i]({south},{west},{north},{east});
        out center tags;
        """
    )
    return buildings + landuse


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


def building_type(tags: dict, name: str) -> str:
    blob = name.lower()
    apartmentish = bool(re.search(r"apartment|mansion|แมนชั่น", blob, re.I))
    condoish = bool(
        re.search(r"condo|condominium|residence|tower|place|suite|court|คอนโด|ทาวเวอร์|เรสซิเดน", blob, re.I)
    ) or tags.get("building") in {"apartments", "condominium"}
    if apartmentish and not condoish:
        return "apartment"
    if condoish:
        return "condo"
    return "other"


def keep(element: dict) -> bool:
    tags = element.get("tags") or {}
    name = (tags.get("name") or tags.get("name:en") or tags.get("name:th") or "").strip()
    if len(name) < 3 or GENERIC_RE.match(name):
        return False
    blob = " ".join(
        tags.get(key) or ""
        for key in ("name", "name:en", "name:th", "alt_name", "tourism", "amenity", "shop", "office")
    )
    if EXCLUDE_RE.search(blob):
        return False
    if tags.get("tourism") in {"hotel", "hostel", "motel", "guest_house"}:
        return False
    if tags.get("amenity") in AMENITY_SKIP:
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
    return value


def record(element: dict) -> dict:
    tags = element.get("tags") or {}
    lat, lng = center(element)
    raw_names = []
    for key in ("name", "name:en", "name:th", "alt_name", "short_name", "official_name", "old_name"):
        raw_names.extend(split_names(tags.get(key)))
    latin = [n for n in raw_names if LATIN_RE.search(n)]
    thai = [n for n in raw_names if THAI_RE.search(n)]
    name_en = tags.get("name:en") or next((n for n in latin if n), None)
    name_th = tags.get("name:th") or next((n for n in thai if n), None)
    display = name_en or tags.get("name") or name_th
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
        "source": "openstreetmap",
        "osm_ref": ref,
    }


def dedupe(elements: list[dict]) -> list[dict]:
    chosen: list[dict] = []
    for element in sorted(elements, key=score, reverse=True):
        point = center(element)
        tags = element.get("tags") or {}
        name = tags.get("name:en") or tags.get("name") or tags.get("name:th") or ""
        folded = fold_name(name)
        if any(
            fold_name((other.get("tags") or {}).get("name:en") or (other.get("tags") or {}).get("name") or "")
            == folded
            and haversine_m(point, center(other)) < 80
            for other in chosen
        ):
            continue
        chosen.append(element)
    return chosen


def build(elements: list[dict]) -> dict:
    unique = {}
    for element in elements:
        if center(element) is None:
            continue
        unique[(element["type"], element["id"])] = element
    kept = [element for element in unique.values() if keep(element)]
    buildings = [record(element) for element in dedupe(kept)]
    buildings.sort(key=lambda item: (item["name"] or "").casefold())
    return {
        "area": {
            "id": "phrom-phong",
            "name": "Phrom Phong",
            "description": (
                "Trial area along Sukhumvit from Soi 23 to Soi 49, "
                "covering the blocks around BTS Phrom Phong and the Asok and Thong Lo edges."
            ),
            "bbox": BBOX,
        },
        "attribution": (
            "© OpenStreetMap contributors. Building names and locations are from "
            "OpenStreetMap, available under the Open Database License (ODbL)."
        ),
        "retrieved_at": date.today().isoformat(),
        "buildings": buildings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--buildings", help="Cached Overpass JSON for named buildings")
    parser.add_argument("--landuse", help="Cached Overpass JSON for residential landuse")
    parser.add_argument("-o", default="data/buildings.json")
    args = parser.parse_args()
    if args.buildings:
        elements = json.load(open(args.buildings))["elements"]
        if args.landuse:
            elements += json.load(open(args.landuse))["elements"]
    else:
        elements = fetch_elements()
    payload = build(elements)
    with open(args.o, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"wrote {len(payload['buildings'])} buildings to {args.o}")


if __name__ == "__main__":
    main()
