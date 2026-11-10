#!/usr/bin/env python3
"""Add the Chao Phraya riverside zone to data/buildings.json.

Residential buildings whose center is within 1.5 km of the Chao Phraya
centerline (OpenStreetMap waterway=river, name แม่น้ำเจ้าพระยา / Chao Phraya)
and inside the Bangkok province boundary (admin_level=4). The buffer is
measured in EPSG:32647 (UTM zone 47N), then clipped to Bangkok, so Nonthaburi,
Samut Prakan, and Pathum Thani stay out.

OpenStreetMap rows use the same residential filters as the station zones.
Condominium projects copied from public FazWaz project pages are added only
when that page publishes a coordinate inside the clipped buffer and the page
calls the project a condo or apartment. Nothing is invented.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, transform, unary_union
from shapely.prepared import prep

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_phrom_phong_buildings as stations  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUFFER_M = 1500
RIVER_RELATION = 227317
BANGKOK_RELATION = 92277
UA_OSM = "thailand-rental-map/1.0 (Chao Phraya riverside zone; ODbL)"
UA_PAGE = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
OVERPASS = (
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass-api.de/api/interpreter",
)
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True).transform
TO_WGS = Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True).transform
ROAD_RE = re.compile(
    r"\d|road|rd\b|soi\b|street|ซอย|ถนน|ทาง",
    re.I,
)
RESIDENTIAL_RE = re.compile(r"condo|condominium|apartment", re.I)
HOTEL_TITLE_RE = re.compile(r"\b(hotel|hostel)\b", re.I)
BY_RE = re.compile(r"\s+by\s+.+$", re.I)
PAREN_RE = re.compile(r"\s*\([^)]*\)\s*")


def project(geom, fn):
    return transform(fn, geom)


def http_bytes(url: str, headers: dict, timeout: int = 45, data: bytes | None = None) -> bytes:
    last: Exception | None = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(last)


def overpass(query: str) -> dict:
    last: Exception | None = None
    for endpoint in OVERPASS:
        try:
            raw = http_bytes(
                endpoint,
                {"User-Agent": UA_OSM, "Content-Type": "text/plain"},
                timeout=180,
                data=query.encode(),
            )
            return json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  overpass fail {endpoint}: {exc}", flush=True)
            time.sleep(3)
    raise RuntimeError(last)


def cached_json(path: Path, query: str) -> dict:
    if path.exists() and path.stat().st_size > 100:
        return json.loads(path.read_text(encoding="utf-8"))
    print(f"fetch {path.name}", flush=True)
    payload = overpass(query)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def member_lines(members: list[dict], roles: set[str] | None) -> list[LineString]:
    lines = []
    for member in members:
        if member.get("type") != "way":
            continue
        if roles is not None and member.get("role") not in roles:
            continue
        coords = [(pt["lon"], pt["lat"]) for pt in member.get("geometry") or []]
        if len(coords) >= 2:
            lines.append(LineString(coords))
    return lines


def as_polygon(element: dict, roles: set[str]):
    lines = member_lines(element.get("members") or [], roles)
    if not lines:
        return None
    polygons = list(polygonize(unary_union(lines)))
    if not polygons:
        return None
    return unary_union(polygons)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def loose_name(value: str) -> str:
    value = BY_RE.sub("", value or "")
    value = PAREN_RE.sub(" ", value)
    return stations.fold_name(value)


def load_zone(cache: Path):
    bangkok = cached_json(
        cache / "bangkok-boundary.json",
        f"""[out:json][timeout:180];
rel({BANGKOK_RELATION});
out geom;
""",
    )["elements"][0]
    river_payload = cached_json(
        cache / "river.json",
        """[out:json][timeout:180];
relation["waterway"="river"]["name"="แม่น้ำเจ้าพระยา"];
out geom;
""",
    )
    river = next(el for el in river_payload["elements"] if el["type"] == "relation")
    districts_payload = cached_json(
        cache / "districts.json",
        f"""[out:json][timeout:180];
rel({BANGKOK_RELATION});
map_to_area -> .bkk;
rel(area.bkk)["boundary"="administrative"]["admin_level"="6"];
out geom;
""",
    )
    bangkok_poly = as_polygon(bangkok, {"outer"})
    river_geom = unary_union(member_lines(river.get("members") or [], None))
    zone_utm = project(river_geom, TO_UTM).buffer(BUFFER_M).intersection(project(bangkok_poly, TO_UTM))
    zone = project(zone_utm, TO_WGS)
    districts = []
    for element in districts_payload["elements"]:
        geom = as_polygon(element, {"outer"})
        if geom is None or geom.is_empty or not zone.intersects(geom):
            continue
        tags = element.get("tags") or {}
        name = (tags.get("name:en") or "").replace(" District", "").strip()
        if not name:
            continue
        districts.append(
            {
                "name": name,
                "name_th": (tags.get("name") or "").replace("เขต", "").strip(),
                "slug": slugify(name),
                "osm_id": f"relation/{element['id']}",
                "geom": geom,
                "prepared": prep(geom),
                "overlap_km2": project(zone.intersection(geom), TO_UTM).area / 1e6,
                "area_km2": project(geom, TO_UTM).area / 1e6,
            }
        )
    districts.sort(key=lambda row: row["name"])
    return zone, prep(zone), districts, river, bangkok


def district_for(lng: float, lat: float, districts: list[dict]) -> dict | None:
    point = Point(lng, lat)
    for district in districts:
        if district["prepared"].covers(point):
            return district
    best = None
    best_d = 1e9
    for district in districts:
        distance = district["geom"].distance(point)
        if distance < best_d:
            best = district
            best_d = distance
    # About 40 m, for a center that lands in a gap between district rings.
    if best is not None and best_d < 0.0004:
        return best
    return None


def area_id(district: dict) -> str:
    return f"chao-phraya-{district['slug']}"


def area_name(district: dict) -> str:
    return f"Chao Phraya Riverside – {district['name']}"


def fetch_osm_tiles(cache: Path, zone) -> list[dict]:
    tile_dir = cache / "osm-tiles"
    tile_dir.mkdir(parents=True, exist_ok=True)
    minx, miny, maxx, maxy = zone.bounds
    step = 0.03
    tiles = []
    y = miny
    while y < maxy - 1e-12:
        x = minx
        y2 = min(y + step, maxy)
        while x < maxx - 1e-12:
            x2 = min(x + step, maxx)
            cell_s, cell_w, cell_n, cell_e = y, x, y2, x2
            if zone.intersects(LineString([(cell_w, cell_s), (cell_e, cell_n)]).envelope):
                from shapely.geometry import box

                if zone.intersects(box(cell_w, cell_s, cell_e, cell_n)):
                    tiles.append((round(cell_s, 6), round(cell_w, 6), round(cell_n, 6), round(cell_e, 6)))
            x += step
        y += step
    elements: list[dict] = []
    for index, (south, west, north, east) in enumerate(tiles):
        dest = tile_dir / f"tile-{index:02d}.json"
        if dest.exists() and dest.stat().st_size > 20:
            payload = json.loads(dest.read_text(encoding="utf-8"))
            print(f"cached tile {index + 1}/{len(tiles)} {len(payload.get('elements') or [])}", flush=True)
        else:
            print(f"fetch tile {index + 1}/{len(tiles)}", flush=True)
            query = f"""[out:json][timeout:90];
(
  nwr["building"~"^(apartments|residential|condominium|house|dormitory|terrace|detached|bungalow)$"]({south},{west},{north},{east});
  nwr["building"]["name"]({south},{west},{north},{east});
  nwr["landuse"="residential"]["name"]({south},{west},{north},{east});
);
out center tags;
"""
            payload = overpass(query)
            dest.write_text(json.dumps(payload), encoding="utf-8")
            time.sleep(1)
        elements.extend(payload.get("elements") or [])
    return elements


def page_headers(referer: str | None = None) -> dict:
    headers = {
        "User-Agent": UA_PAGE,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        headers["Referer"] = referer
    return headers


def load_directory_urls(cache: Path) -> list[str]:
    dest = cache / "project-directory.xml"
    if not dest.exists():
        raw = http_bytes(
            "https://www.fazwaz.com/sitemaps/www.fazwaz.com-project-directory.xml",
            page_headers(),
        )
        dest.write_bytes(raw)
    text = dest.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"<loc>(https://www\.fazwaz\.com/project-directory/thailand/bangkok/[^<]+)</loc>", text)


def fetch_text(url: str, cache: Path, kind: str) -> str | None:
    folder = cache / kind
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", url)[-180:]
    dest = folder / safe
    if dest.exists() and dest.stat().st_size > 50:
        return dest.read_text(encoding="utf-8", errors="replace")
    try:
        raw = http_bytes(url, page_headers(url.split("?")[0]), timeout=50)
    except Exception as exc:  # noqa: BLE001
        print(f"  fail {url}: {exc}", flush=True)
        return None
    text = raw.decode("utf-8", "replace")
    dest.write_text(text, encoding="utf-8")
    return text


def directory_projects(html: str) -> list[tuple[str, str]]:
    found = []
    for url, name in re.findall(
        r'href="(https://www\.fazwaz\.com/projects/[^"]+)"[\s\S]{0,900}?class="project-header">([^<]+)',
        html,
    ):
        found.append((url.split("?")[0].rstrip("/"), re.sub(r"\s+", " ", name).strip()))
    if found:
        return found
    for url in re.findall(r"https://www\.fazwaz\.com/projects/thailand/bangkok/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+", html):
        found.append((url.rstrip("/"), ""))
    return found


def marker_points(html_or_json: str) -> list[dict]:
    try:
        payload = json.loads(html_or_json)
    except json.JSONDecodeError:
        return []
    points = []
    for marker in payload.get("markers") or []:
        coords = (marker.get("point") or {}).get("coordinates") or []
        if len(coords) != 2:
            continue
        lng, lat = coords
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        points.append(
            {
                "unit_id": marker.get("id"),
                "lat": float(lat),
                "lng": float(lng),
                "icon": marker.get("icon") or "",
            }
        )
    return points


def parse_project(html: str, url: str) -> dict | None:
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    graph = data.get("@graph") if isinstance(data, dict) else None
    if not isinstance(graph, list):
        return None
    node = None
    for item in graph:
        if not isinstance(item, dict) or not item.get("geo"):
            continue
        if item.get("@type") in {"Organization", "RealEstateAgent"}:
            continue
        node = item
        break
    if node is None:
        return None
    geo = node.get("geo") or {}
    try:
        lat = float(geo["latitude"])
        lng = float(geo["longitude"])
    except (TypeError, ValueError, KeyError):
        return None
    name = re.sub(r"\s+", " ", str(node.get("name") or "")).strip()
    if len(name) < 3:
        return None
    title_match = re.search(r"<title>(.*?)</title>", html, re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", title_match.group(1) if title_match else "")).strip()
    pid_match = re.search(r'"project_id"\s*:\s*(\d+)', html)
    project_id = pid_match.group(1) if pid_match else None
    street = ""
    address = node.get("address")
    if isinstance(address, dict):
        street = re.sub(r"\s+", " ", str(address.get("streetAddress") or "")).strip()
    return {
        "url": url,
        "name": name,
        "title": title,
        "lat": lat,
        "lng": lng,
        "project_id": project_id,
        "street": street,
        "html_head": html[:120000],
    }


def residential_project(page: dict) -> bool:
    title = page["title"]
    name = page["name"]
    blob = f"{title} {name}"
    if HOTEL_TITLE_RE.search(title) and not RESIDENTIAL_RE.search(title):
        return False
    if RESIDENTIAL_RE.search(blob):
        return True
    if re.search(r"mixed[-\s]?use", title, re.I):
        return bool(RESIDENTIAL_RE.search(page["html_head"]))
    return False


def usable_street(street: str) -> str | None:
    """Street line from the project page. Plus codes, bus stops, and postcode-only lines are omitted."""
    street = re.sub(r"\s+", " ", street).strip(" ,")
    street = re.sub(r"\b[A-Z0-9]{4}\+[A-Z0-9]{2,}\b,?\s*", "", street).strip(" ,")
    if len(street) < 8 or "ป้ายรถ" in street:
        return None
    if re.search(r"\b(road|rd|soi|street|alley|avenue|ave|thanon)\b|ซอย|ถนน|(?<![\u0e00-\u0e7f])ถ\.", street, re.I):
        return street
    numbers = [number for number in re.findall(r"\d+", street) if len(number) != 5]
    if not numbers:
        return None
    return street


class DirectoryIndex:
    def __init__(self, buildings: list[dict]):
        self.ids = set()
        self.urls = set()
        self.names: list[tuple[str, float, float]] = []
        for building in buildings:
            self.add(building)

    def add(self, building: dict) -> None:
        self.ids.add(building["id"])
        if building.get("osm_ref"):
            self.ids.add(building["osm_ref"])
        url = (building.get("source_url") or "").split("?")[0].rstrip("/")
        if url:
            self.urls.add(url)
        lat, lng = building["lat"], building["lng"]
        for value in [building.get("name"), building.get("name_en"), building.get("name_th"), *(building.get("aliases") or [])]:
            folded = stations.fold_name(value or "")
            loose = loose_name(value or "")
            if len(folded) >= 3:
                self.names.append((folded, loose, lat, lng))

    def name_hit(self, name: str, lat: float, lng: float) -> bool:
        folded = stations.fold_name(name)
        loose = loose_name(name)
        point = (lat, lng)
        for other_fold, other_loose, other_lat, other_lng in self.names:
            distance = stations.haversine_m(point, (other_lat, other_lng))
            if folded and folded == other_fold and distance < 80:
                return True
            # "D BURA" and "dBURA" published about 84 m apart.
            if len(loose) >= 8 and loose == other_loose and distance < 120:
                return True
        return False


def collect_fazwaz(cache: Path, zone_prepared, districts: list[dict]) -> tuple[list[dict], dict]:
    stats = Counter()
    district_slugs = {row["slug"] for row in districts}
    directory_urls = [
        url
        for url in load_directory_urls(cache)
        if len(url.split("/")) >= 7 and url.split("/")[6] in district_slugs
    ]
    print(f"fazwaz directory pages {len(directory_urls)}", flush=True)
    known: dict[str, str] = {}
    by_name: dict[str, list[str]] = defaultdict(list)

    def read_directory(url: str) -> list[tuple[str, str]]:
        html = fetch_text(url, cache, "fazwaz-dir")
        if not html:
            stats["directory_failed"] += 1
            return []
        return directory_projects(html)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(read_directory, url) for url in directory_urls]
        for future in as_completed(futures):
            for project_url, name in future.result():
                known[project_url] = name
                if name:
                    by_name[stations.fold_name(name)].append(project_url)
                    loose = loose_name(name)
                    if loose:
                        by_name[loose].append(project_url)
    print(f"fazwaz directory projects {len(known)}", flush=True)

    marker_urls = []
    for district in districts:
        for kind in ("condo-for-sale", "condo-for-rent", "apartment-for-rent"):
            marker_urls.append(
                f"https://www.fazwaz.com/{kind}/thailand/bangkok/{district['slug']}?action=markers"
            )
    markers = []
    seen_units = set()

    def read_markers(url: str) -> list[dict]:
        text = fetch_text(url, cache, "fazwaz-markers")
        if not text:
            stats["marker_failed"] += 1
            return []
        return marker_points(text)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(read_markers, url) for url in marker_urls]
        for future in as_completed(futures):
            for marker in future.result():
                if marker["icon"] not in {"condo", "apartment"}:
                    stats["marker_other_icon"] += 1
                    continue
                if marker["unit_id"] in seen_units:
                    continue
                seen_units.add(marker["unit_id"])
                if not zone_prepared.covers(Point(marker["lng"], marker["lat"])):
                    stats["marker_outside"] += 1
                    continue
                markers.append(marker)
    print(f"fazwaz in-zone markers {len(markers)}", flush=True)

    def marker_name(marker: dict) -> str:
        if not marker.get("unit_id"):
            return ""
        url = (
            "https://www.fazwaz.com/api/units/marker-detail"
            f"?unit_id={marker['unit_id']}&sale_type=forsale"
        )
        text = fetch_text(url, cache, "fazwaz-marker-detail")
        if not text:
            stats["marker_detail_failed"] += 1
            return ""
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return ""
        if not isinstance(payload, dict):
            return ""
        return re.sub(r"\s+", " ", str(payload.get("name") or "")).strip()

    names: dict[int, str] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(marker_name, marker): marker for marker in markers}
        for future in as_completed(futures):
            marker = futures[future]
            names[id(marker)] = future.result()

    wanted: dict[str, str] = {}
    # Directory pages in districts that are mostly inside the buffer. Partial
    # districts contribute through in-zone markers so a Bang Na project 4 km
    # from the river is not fetched.
    mostly_inside = {
        row["slug"]
        for row in districts
        if row["overlap_km2"] >= 2.5 or (row["area_km2"] and row["overlap_km2"] / row["area_km2"] >= 0.5)
    }
    for url, name in known.items():
        parts = url.split("/")
        district_slug = parts[6] if len(parts) > 6 else ""
        if district_slug in mostly_inside:
            wanted[url] = name
    for marker in markers:
        name = names.get(id(marker)) or ""
        urls = []
        if name:
            urls = by_name.get(stations.fold_name(name)) or by_name.get(loose_name(name)) or []
        if urls:
            for url in urls:
                wanted.setdefault(url, name)
            continue
        if not marker.get("unit_id"):
            stats["marker_unmatched"] += 1
            continue
        redirect = f"https://www.fazwaz.com/api/redirect?type=unit&lang=en&id={marker['unit_id']}&sale_type=forsale"
        try:
            # The redirect target is the public unit page, which links to the project.
            request = urllib.request.Request(redirect, headers=page_headers())
            with urllib.request.urlopen(request, timeout=40) as response:
                final = response.geturl()
        except Exception:  # noqa: BLE001
            stats["marker_unmatched"] += 1
            continue
        page = fetch_text(final, cache, "fazwaz-unit")
        if not page:
            stats["marker_unmatched"] += 1
            continue
        links = re.findall(r"https://www\.fazwaz\.com/projects/thailand/[^\"\s<]+", page)
        if not links:
            stats["marker_unmatched"] += 1
            continue
        wanted.setdefault(links[0].split("?")[0].rstrip("/"), name)
    print(f"fazwaz project pages to read {len(wanted)}", flush=True)

    pages = []

    def read_project(url: str) -> dict | None:
        html = fetch_text(url, cache, "fazwaz-project")
        if not html:
            stats["project_failed"] += 1
            return None
        return parse_project(html, url)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(read_project, url) for url in wanted]
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 50 == 0:
                print(f"  project pages {done}/{len(wanted)}", flush=True)
            page = future.result()
            if page:
                pages.append(page)
    stats["project_pages"] = len(pages)
    return pages, stats


def fazwaz_row(page: dict, district: dict) -> dict:
    name = page["name"]
    kind = "apartment" if re.search(r"apartment|mansion|แมนชั่น", name, re.I) and not re.search(
        r"condo|condominium|residence|คอนโด", name, re.I
    ) else "condo"
    if page["project_id"]:
        row_id = f"fazwaz-{page['project_id']}"
    else:
        row_id = "fazwaz-" + page["url"].rstrip("/").split("/")[-1]
    areas = stations.areas_for(page["lat"], page["lng"])
    zone = area_id(district)
    if zone not in areas:
        areas.append(zone)
    row = {
        "id": row_id,
        "name": name,
        "name_en": name,
        "name_th": None,
        "aliases": [],
        "type": kind,
        "lat": round(page["lat"], 7),
        "lng": round(page["lng"], 7),
        "areas": areas,
        "named": True,
        "source": "fazwaz",
        "osm_ref": "",
        "source_url": page["url"],
    }
    street = usable_street(page["street"])
    if street:
        row["address"] = street
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", default="/tmp/chao-phraya")
    parser.add_argument("--base", default=str(ROOT / "data/buildings.json"))
    parser.add_argument("-o", default=str(ROOT / "data/buildings.json"))
    parser.add_argument("--skip-fazwaz", action="store_true")
    args = parser.parse_args()
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    zone, zone_prepared, districts, river, bangkok = load_zone(cache)
    print(
        f"zone km2 {project(zone, TO_UTM).area / 1e6:.2f} districts {len(districts)} "
        f"river relation/{river['id']} bangkok relation/{bangkok['id']}",
        flush=True,
    )
    # A Nonthaburi riverside point must stay outside the clipped zone.
    if zone_prepared.covers(Point(100.49, 13.86)):
        raise SystemExit("zone clipped incorrectly: Nonthaburi point is inside")
    if not zone_prepared.covers(Point(100.514223, 13.7188128)):
        raise SystemExit("Saphan Taksin is outside the river zone")

    elements = fetch_osm_tiles(cache, zone)
    unique = {}
    for element in elements:
        if stations.center(element) is None:
            continue
        unique[(element["type"], element["id"])] = element
    ordered = sorted(unique.values(), key=stations.score, reverse=True)
    print(f"osm elements {len(ordered)}", flush=True)

    payload = json.loads(Path(args.base).read_text(encoding="utf-8"))
    buildings = payload["buildings"]
    index = DirectoryIndex(buildings)
    stats = Counter()
    per_district = defaultdict(lambda: Counter())
    added_osm = []

    for building in buildings:
        point = Point(building["lng"], building["lat"])
        if not zone_prepared.covers(point):
            continue
        district = district_for(building["lng"], building["lat"], districts)
        if district is None:
            stats["existing_no_district"] += 1
            continue
        zone_area = area_id(district)
        if zone_area not in building["areas"]:
            building["areas"] = list(building["areas"]) + [zone_area]
            stats["existing_retagged"] += 1
            per_district[district["name"]]["retagged"] += 1

    for element in ordered:
        lat, lng = stations.center(element)
        if not zone_prepared.covers(Point(lng, lat)):
            continue
        if not stations.include_element(element):
            continue
        district = district_for(lng, lat, districts)
        if district is None:
            stats["osm_no_district"] += 1
            continue
        item = stations.record(element)
        zone_area = area_id(district)
        if zone_area not in item["areas"]:
            item["areas"] = list(item["areas"]) + [zone_area]
        if item["id"] in index.ids or item["osm_ref"] in index.ids:
            stats["osm_dup_id"] += 1
            continue
        if index.name_hit(item["name"], item["lat"], item["lng"]):
            stats["osm_dup_name"] += 1
            continue
        index.add(item)
        added_osm.append(item)
        stats["osm_new"] += 1
        if item.get("named"):
            stats["osm_new_named"] += 1
        else:
            stats["osm_new_address"] += 1
        per_district[district["name"]]["osm"] += 1

    fazwaz_stats: Counter = Counter()
    added_fazwaz = []
    if not args.skip_fazwaz:
        pages, fazwaz_stats = collect_fazwaz(cache, zone_prepared, districts)
        for page in pages:
            point = Point(page["lng"], page["lat"])
            if not zone_prepared.covers(point):
                fazwaz_stats["outside"] += 1
                continue
            if not residential_project(page):
                fazwaz_stats["not_residential"] += 1
                continue
            district = district_for(page["lng"], page["lat"], districts)
            if district is None:
                fazwaz_stats["no_district"] += 1
                continue
            row = fazwaz_row(page, district)
            if row["id"] in index.ids:
                # Same numeric id already stored for a different page keeps a slug id.
                if row["source_url"] not in index.urls:
                    slug_id = "fazwaz-" + row["source_url"].rstrip("/").split("/")[-1]
                    if slug_id not in index.ids:
                        row["id"] = slug_id
                    else:
                        fazwaz_stats["dup_id"] += 1
                        continue
                else:
                    fazwaz_stats["dup_url"] += 1
                    continue
            if row["source_url"] in index.urls:
                fazwaz_stats["dup_url"] += 1
                continue
            if index.name_hit(row["name"], row["lat"], row["lng"]):
                fazwaz_stats["dup_name"] += 1
                continue
            index.add(row)
            added_fazwaz.append(row)
            fazwaz_stats["added"] += 1
            per_district[district["name"]]["fazwaz"] += 1

    buildings.extend(added_osm)
    buildings.extend(added_fazwaz)
    buildings.sort(key=lambda item: (item.get("name") or "").casefold())

    area_rows = []
    for district in districts:
        count = sum(per_district[district["name"]].values())
        if count == 0:
            continue
        area_rows.append(
            {
                "id": area_id(district),
                "name": area_name(district),
                "kind": "river-buffer",
                "corridor": "chao-phraya",
                "buffer_m": BUFFER_M,
                "description": (
                    f"Residential buildings within {BUFFER_M} m of the Chao Phraya River "
                    f"(OpenStreetMap relation/{river['id']}, {river.get('tags', {}).get('name')}) "
                    f"and inside Bangkok (relation/{bangkok['id']}), in {district['name']} "
                    f"({district['osm_id']}). The buffer is measured in EPSG:32647 and clipped "
                    "to the Bangkok boundary."
                ),
                "district": {
                    "name": district["name"],
                    "name_th": district["name_th"],
                    "osm_id": district["osm_id"],
                },
            }
        )
    kept_ids = {row["id"] for row in area_rows}
    for building in buildings:
        building["areas"] = [area for area in building["areas"] if not str(area).startswith("chao-phraya-") or area in kept_ids]

    previous_areas = [area for area in payload.get("areas") or [] if area.get("id") in stations.STATIONS]
    payload["areas"] = previous_areas + area_rows
    south, west, north, east = zone.bounds[1], zone.bounds[0], zone.bounds[3], zone.bounds[2]
    bbox = payload["area"]["bbox"]
    bbox["south"] = min(bbox["south"], south)
    bbox["west"] = min(bbox["west"], west)
    bbox["north"] = max(bbox["north"], north)
    bbox["east"] = max(bbox["east"], east)
    payload["area"]["name"] = (
        "Sukhumvit (Nana–Bearing), Ari, Silom–Sathorn, Bang Na (BITEC), central Bangkok, "
        "and the Chao Phraya riverside"
    )
    payload["area"]["description"] = (
        "Every residential building within 2.5 km of a BTS Sukhumvit station "
        "from Nana (E3) through Bearing (E14), within 2.5 km of BTS Ari, "
        "within 2.5 km of BTS Sala Daeng (Silom–Sathorn), and within 2.5 km "
        "of BITEC in Bang Na. Named residential buildings within 2.5 km of MRT Phra Ram 9, "
        "BTS Phaya Thai, BTS Ratchathewi, BTS Chit Lom, BTS Phloen Chit, MRT Lumphini, "
        "and BTS Saphan Taksin (Riverside / Charoen Krung) are included too. "
        "Also every residential building within 1.5 km of the Chao Phraya River whose "
        "center is inside Bangkok (the buffer is EPSG:32647, clipped to the Bangkok "
        "admin_level=4 boundary, so Nonthaburi, Samut Prakan, and Pathum Thani are excluded). "
        "A building in more than one area is stored once. Condominium projects inside these "
        "areas that were not already in OpenStreetMap were added from public FazWaz project "
        "pages, with that page's coordinates."
    )
    payload["retrieved_at"] = date.today().isoformat()
    payload["buildings"] = buildings
    Path(args.o).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "buildings": len(buildings),
        "osm_added": stats["osm_new"],
        "osm_added_named": stats["osm_new_named"],
        "osm_added_address": stats["osm_new_address"],
        "osm_dup_id": stats["osm_dup_id"],
        "osm_dup_name": stats["osm_dup_name"],
        "existing_retagged": stats["existing_retagged"],
        "fazwaz_added": fazwaz_stats.get("added", 0),
        "fazwaz": {key: fazwaz_stats[key] for key in fazwaz_stats},
        "districts": {
            name: dict(counts)
            for name, counts in sorted(per_district.items())
        },
        "zone_km2": round(project(zone, TO_UTM).area / 1e6, 2),
        "river": f"relation/{river['id']}",
        "bangkok": f"relation/{bangkok['id']}",
    }
    (cache / "stats.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {args.o}")


if __name__ == "__main__":
    main()
