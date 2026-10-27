#!/usr/bin/env python3
"""Build data/buildings.json for the Sukhumvit corridor, Ari, and Silom–Sathorn.

Sukhumvit is every residential building whose center is within 2.5 km of a
BTS station from Nana (E3) through Bearing (E14). Ari and Silom–Sathorn stay
2.5 km radii around BTS Ari and BTS Sala Daeng. Station coordinates are the
OpenStreetMap railway=station nodes. Buildings in more than one station area
are stored once and list every area they fall in. Unnamed buildings are
included only when the address is specific enough to label them.
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

RADIUS_M = 2500


def station(id, name, osm_name, name_th, ref, osm_id, lat, lng, corridor, detail=None):
    row = {
        "id": id,
        "name": name,
        "osm_name": osm_name,
        "name_th": name_th,
        "ref": ref,
        "osm_id": osm_id,
        "lat": lat,
        "lng": lng,
        "corridor": corridor,
    }
    if detail:
        row["detail"] = detail
    return row


# Sukhumvit line order, Nana (E3) through Bearing (E14), then Ari and Silom–Sathorn.
# Coordinates are OpenStreetMap railway=station nodes.
STATIONS = {
    "nana": station("nana", "Nana", "Nana", "นานา", "E3", "node/5391628766", 13.7405358, 100.5554291, "sukhumvit"),
    "asok": station("asok", "Asok", "Asok", "อโศก", "E4", "node/5391625873", 13.7370432, 100.5603571, "sukhumvit", "interchange with MRT Sukhumvit"),
    "phrom-phong": station("phrom-phong", "Phrom Phong", "Phrom Phong", "พร้อมพงษ์", "E5", "node/5391626093", 13.7304345, 100.5697129, "sukhumvit"),
    "thong-lo": station("thong-lo", "Thong Lo", "Thong Lo", "ทองหล่อ", "E6", "node/5391626092", 13.7242264, 100.5785054, "sukhumvit"),
    "ekamai": station("ekamai", "Ekamai", "Ekkamai", "เอกมัย", "E7", "node/5405616025", 13.7195385, 100.585111, "sukhumvit", "Ekamai zone, Sukhumvit Soi 63"),
    "phra-khanong": station("phra-khanong", "Phra Khanong", "Phra Khanong", "พระโขนง", "E8", "node/5391610985", 13.7151693, 100.5912365, "sukhumvit"),
    "on-nut": station("on-nut", "On Nut", "On Nut", "อ่อนนุช", "E9", "node/5391620400", 13.7056249, 100.601004, "sukhumvit"),
    "bang-chak": station("bang-chak", "Bang Chak", "Bang Chak", "บางจาก", "E10", "node/5391618414", 13.6967594, 100.6053402, "sukhumvit"),
    "punnawithi": station("punnawithi", "Punnawithi", "Punnawithi", "ปุณณวิถี", "E11", "node/5391616767", 13.689279, 100.6089963, "sukhumvit"),
    "udom-suk": station("udom-suk", "Udom Suk", "Udom Suk", "อุดมสุข", "E12", "node/5391613497", 13.6798746, 100.6094698, "sukhumvit"),
    "bang-na": station("bang-na", "Bang Na", "Bang Na", "บางนา", "E13", "node/5391610964", 13.668138, 100.6046633, "sukhumvit"),
    "bearing": station("bearing", "Bearing", "Bearing", "แบริ่ง", "E14", "node/5391599348", 13.6611846, 100.6018056, "sukhumvit"),
    "ari": station("ari", "Ari", "Ari", "อารีย์", "N5", "node/5388607091", 13.7797077, 100.5446201, "ari"),
    "silom-sathorn": station("silom-sathorn", "Silom–Sathorn", "Sala Daeng", "ศาลาแดง", "S2", "node/451697335", 13.7285677, 100.5343416, "silom-sathorn", "interchange with MRT Si Lom"),
}
AREA_IDS = list(STATIONS)
SUKHUMVIT_IDS = [key for key, row in STATIONS.items() if row["corridor"] == "sukhumvit"]
UA = "thailand-rental-map/1.0 (Sukhumvit building directory; ODbL)"
# The German public instance often returns 504 on a dense 2.5 km query.
# Try the French mirror first, then the main instance, then smaller tiles.
OVERPASS_ENDPOINTS = (
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass-api.de/api/interpreter",
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


def areas_for(lat: float, lng: float) -> list[str]:
    point = (lat, lng)
    return [
        key
        for key, row in STATIONS.items()
        if haversine_m(point, (row["lat"], row["lng"])) <= RADIUS_M
    ]


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
        if any(area in SUKHUMVIT_IDS for area in areas):
            counts["sukhumvit"] = counts.get("sukhumvit", 0) + 1
        for area in areas:
            if area in counts:
                counts[area] += 1
    return counts


def stamp_existing(building: dict) -> dict:
    """Keep a directory building and refresh which station areas its center falls in."""
    areas = areas_for(building["lat"], building["lng"])
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
    boxes = [circle_bbox(row["lat"], row["lng"]) for row in STATIONS.values()]
    return {
        "area": {
            "id": "bangkok",
            "name": "Sukhumvit (Nana–Bearing), Ari and Silom–Sathorn",
            "description": (
                "Every residential building within 2.5 km of a BTS Sukhumvit station "
                "from Nana (E3) through Bearing (E14), within 2.5 km of BTS Ari, and "
                "within 2.5 km of BTS Sala Daeng (Silom–Sathorn). A building in more "
                "than one station area is stored once."
            ),
            "bbox": union_bbox(boxes),
        },
        "areas": [
            {
                "id": row["id"],
                "name": row["name"],
                "kind": "radius",
                "corridor": row["corridor"],
                "radius_m": RADIUS_M,
                "description": station_description(row),
                "station": {
                    "name": row["osm_name"],
                    "name_th": row["name_th"],
                    "ref": row["ref"],
                    "osm_id": row["osm_id"],
                    "lat": row["lat"],
                    "lng": row["lng"],
                },
            }
            for row in STATIONS.values()
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


def count_rows(rows: list[dict], skipped_n: int) -> str:
    from collections import Counter

    types = Counter(b["type"] for b in rows)
    named = sum(1 for b in rows if b["named"])
    address = sum(1 for b in rows if not b["named"])
    return (
        f"{len(rows)} named={named} address={address} "
        f"condo={types['condo']} apartment={types['apartment']} other={types['other']} "
        f"skipped_unnamed={skipped_n}"
    )


def summarize(payload: dict, skipped: dict[str, int]) -> None:
    buildings = payload["buildings"]
    print(f"unique {len(buildings)}")
    print("skipped unnamed", json.dumps(skipped, ensure_ascii=False))
    for area in AREA_IDS:
        rows = [b for b in buildings if area in b["areas"]]
        print(f"{area}: {count_rows(rows, skipped.get(area, 0))}")
    suk = [b for b in buildings if any(area in SUKHUMVIT_IDS for area in b["areas"])]
    print(f"sukhumvit-corridor: {count_rows(suk, skipped.get('sukhumvit', 0))}")
    print(f"multi-station {sum(1 for b in buildings if len(b['areas']) > 1)}")


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
