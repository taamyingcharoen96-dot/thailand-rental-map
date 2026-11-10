#!/usr/bin/env python3
"""Fetch Bangkok urban-rail lines and stations from OpenStreetMap.

Writes data/transit_lines.geojson and data/transit_stations.json.
Coordinates are copied from Overpass. Nothing is interpolated except a
join shorter than 40 m between two OSM way endpoints, and Douglas-Peucker
simplification of the drawn line.

Operating lines:
  BTS Sukhumvit, BTS Silom, BTS Gold,
  MRT Blue (including the Tha Phra loop), MRT Purple, MRT Yellow,
  MRT Pink (including the Muang Thong Thani branch),
  Airport Rail Link, SRT Dark Red, SRT Light Red.

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

ROOT = Path(__file__).resolve().parents[1]
UA = "thailand-rental-map/1.0 (Bangkok transit overlay; ODbL)"
OVERPASS_ENDPOINTS = (
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
# Bangkok metro, from Kheha / Lak Song in the south to Rangsit in the north,
# and from Taling Chan / Khlong Bang Phai in the west to Suvarnabhumi in the east.
BBOX = (13.48, 100.22, 14.18, 100.98)
JOIN_M = 40.0
SIMPLIFY_DEG = 0.00008  # about 9 m
# Only platforms of the same station (Siam, Tao Poon, Phaya Thai) share a
# marker. Wider interchanges such as Asok and Sukhumvit stay on their own
# coordinates so the dot sits on that line.
MERGE_M = 80.0
# Farther interchange pairs stay as separate markers so neither station is
# moved, but both are flagged. 450 m reaches Phahon Yothin / Ha Yaek Lat Phrao
# (about 430 m between the OSM station nodes) and stops short of the next
# cross-line pair, Kamphaeng Phet / Saphan Khwai at about 500 m, which is not
# an interchange.
LINK_M = 450.0
# Same English name on two lines (Nonthaburi Civic Center, Hua Mak).
SAME_NAME_LINK_M = 700.0
NEAR_LINE_M = 90.0

# Official colours below are the fallback when a route has no OSM colour tag.
# The script prefers the colour tag on the longest operating route of the line.
CANON = {
    "bts-sukhumvit": {
        "name_en": "BTS Sukhumvit",
        "name_th": "รถไฟฟ้าบีทีเอส สายสุขุมวิท",
        "short": "Sukhumvit",
        "color": "#65B724",
        "prefixes": ("CEN", "N", "E"),
    },
    "bts-silom": {
        "name_en": "BTS Silom",
        "name_th": "รถไฟฟ้าบีทีเอส สายสีลม",
        "short": "Silom",
        "color": "#02817D",
        "prefixes": ("W", "S"),
    },
    "bts-gold": {
        "name_en": "BTS Gold",
        "name_th": "รถไฟฟ้าบีทีเอส สายสีทอง",
        "short": "Gold",
        "color": "#A58704",
        "prefixes": ("G",),
    },
    "mrt-blue": {
        "name_en": "MRT Blue",
        "name_th": "รถไฟฟ้ามหานคร สายสีน้ำเงิน",
        "short": "Blue",
        "color": "#1E398D",
        "prefixes": ("BL",),
    },
    "mrt-purple": {
        "name_en": "MRT Purple",
        "name_th": "รถไฟฟ้ามหานคร สายสีม่วง",
        "short": "Purple",
        "color": "#893B90",
        "prefixes": ("PP",),
    },
    "mrt-yellow": {
        "name_en": "MRT Yellow",
        "name_th": "รถไฟฟ้ามหานคร สายสีเหลือง",
        "short": "Yellow",
        "color": "#FFD400",
        "prefixes": ("YL",),
    },
    "mrt-pink": {
        "name_en": "MRT Pink",
        "name_th": "รถไฟฟ้ามหานคร สายสีชมพู",
        "short": "Pink",
        "color": "#E76589",
        "prefixes": ("PK", "MT"),
    },
    "arl": {
        "name_en": "Airport Rail Link",
        "name_th": "รถไฟฟ้าแอร์พอร์ต เรล ลิงก์",
        "short": "Airport Rail Link",
        "color": "#59191F",
        "prefixes": ("A",),
    },
    "srt-dark-red": {
        "name_en": "SRT Dark Red",
        "name_th": "รถไฟฟ้าชานเมือง สายสีแดงเข้ม",
        "short": "Dark Red",
        "color": "#B5191E",
        "prefixes": ("RN", "RE"),
    },
    "srt-light-red": {
        "name_en": "SRT Light Red",
        "name_th": "รถไฟฟ้าชานเมือง สายสีแดงอ่อน",
        "short": "Light Red",
        "color": "#FC5353",
        "prefixes": ("RW",),
    },
}
LINE_ORDER = list(CANON)

THAI_RE = re.compile(r"[\u0e00-\u0e7f]")
LATIN_RE = re.compile(r"[A-Za-z]")
CODE_RE = re.compile(r"^(?:CEN|[A-Z]{1,4}\d{1,3})$")
DEPOT_RE = re.compile(
    r"depot|stabling|\byard\b|workshop|อู่ซ่อม|ศูนย์ซ่อม|โรงซ่อม|ทางวิ่งทดสอบ",
    re.I,
)
SKIP_RAIL = {"abandoned", "disused", "razed", "proposed", "construction"}


def overpass(query: str) -> dict:
    last_error: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        host = endpoint.split("/")[2]
        try:
            req = urllib.request.Request(
                endpoint, data=query.encode(), headers={"User-Agent": UA}
            )
            with urllib.request.urlopen(req, timeout=240) as response:
                payload = json.load(response)
            print(f"  ok {host}", flush=True)
            return payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            last_error = exc
            print(f"  fail {host}: {exc}", flush=True)
            time.sleep(3)
    raise RuntimeError(last_error)


def bbox_clause() -> str:
    south, west, north, east = BBOX
    return f"({south},{west},{north},{east})"


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def xy(lat: float, lon: float) -> tuple[float, float]:
    return (
        lon * 111320.0 * math.cos(math.radians(13.8)),
        lat * 110540.0,
    )


def dist_point_seg(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_to_lines(lat: float, lon: float, segments: list[list[tuple[float, float]]]) -> float:
    p = xy(lat, lon)
    best = float("inf")
    for seg in segments:
        if len(seg) < 2:
            continue
        prev = xy(seg[0][0], seg[0][1])
        for lat2, lon2 in seg[1:]:
            cur = xy(lat2, lon2)
            best = min(best, dist_point_seg(p, prev, cur))
            prev = cur
            if best < 15:
                return best
    return best


def hex_color(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip()
    if raw.startswith("#"):
        raw = raw[1:]
    if re.fullmatch(r"[0-9A-Fa-f]{6}", raw):
        return "#" + raw.upper()
    if re.fullmatch(r"[0-9A-Fa-f]{3}", raw):
        return "#" + "".join(ch * 2 for ch in raw).upper()
    return None


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def name_en(tags: dict) -> str:
    for key in ("name:en", "alt_name:en", "official_name:en", "int_name"):
        text = clean(tags.get(key))
        if text:
            return text
    text = clean(tags.get("name"))
    if text and LATIN_RE.search(text):
        return text
    return ""


def name_th(tags: dict) -> str:
    for key in ("name:th", "alt_name:th", "official_name:th"):
        text = clean(tags.get(key))
        if text:
            return text
    text = clean(tags.get("name"))
    if text and THAI_RE.search(text) and not LATIN_RE.search(text):
        return text
    return ""


def norm_name(value: str) -> str:
    return re.sub(r"[^a-z0-9\u0e00-\u0e7f]+", "", (value or "").lower())


def codes_in(ref: str | None) -> list[str]:
    found = []
    for part in re.split(r"[;,|/]", ref or ""):
        code = part.strip().upper().replace(" ", "")
        if CODE_RE.match(code):
            found.append(code)
    return found


def code_line(code: str) -> str | None:
    best = None
    best_len = -1
    for line_id, meta in CANON.items():
        for prefix in meta["prefixes"]:
            if code == prefix or (code.startswith(prefix) and code[len(prefix):].isdigit()):
                if len(prefix) > best_len:
                    best = line_id
                    best_len = len(prefix)
    return best


def code_for_line(codes: list[str], line_id: str) -> str | None:
    for code in codes:
        # Siam's OSM ref is CEN on both BTS lines.
        if code == "CEN" and line_id in {"bts-sukhumvit", "bts-silom"}:
            return code
        if code_line(code) == line_id:
            return code
    return None


def stop_members(relation: dict) -> list[dict]:
    members = [m for m in relation.get("members") or [] if m.get("type") == "node"]
    stops = [m for m in members if m.get("role") in {"stop", "stop_entry_only", "stop_exit_only"}]
    if stops:
        return stops
    platforms = [m for m in members if m.get("role") == "platform"]
    if platforms:
        return platforms
    # SRT Light Red tags its stop_position nodes with an empty role.
    return [m for m in members if not m.get("role")]


def passenger_station(tags: dict) -> bool:
    railway = tags.get("railway") or ""
    station = tags.get("station") or ""
    if railway in SKIP_RAIL or station in SKIP_RAIL:
        return False
    if tags.get("disused:railway") or tags.get("abandoned:railway") or tags.get("proposed:railway"):
        return False
    if str(tags.get("construction") or "") in {"yes", "station"}:
        return False
    blob = " ".join(tags.get(key) or "" for key in ("name", "name:en", "name:th"))
    if DEPOT_RE.search(blob):
        return False
    return True


def classify(tags: dict) -> str | None:
    route = tags.get("route") or ""
    if route not in {"subway", "light_rail", "monorail", "train"}:
        return None
    if tags.get("construction") or tags.get("state") in {"proposed", "construction", "abandoned"}:
        return None
    ref = tags.get("ref") or ""
    network = tags.get("network") or ""
    blob = " ".join(
        tags.get(key) or ""
        for key in ("name", "name:en", "name:th", "ref", "network")
    )
    # Short-turn workings repeat track already covered by the full line.
    if "ขบวนเสริม" in blob:
        return None
    if ref in {"สุขุมวิท", "BTS-สุขุมวิท"} or "สายสุขุมวิท" in blob or "Sukhumvit" in blob:
        return "bts-sukhumvit"
    if ref in {"สีลม", "BTS-สีลม"} or "สายสีลม" in blob or "Silom" in blob:
        return "bts-silom"
    if "Gold" in ref or "สีทอง" in blob or "Gold Line" in blob:
        return "bts-gold"
    if ref in {"MRT-BL", "BL"} or "สายสีน้ำเงิน" in blob or "Blue Line" in blob:
        if "Metropolitan" in network or network in {"MRT", "Metropolitan Rapid Transit"} or "น้ำเงิน" in blob:
            return "mrt-blue"
    if ref == "MRT Purple" or "สายสีม่วง" in blob or "Purple Line" in blob:
        return "mrt-purple"
    if ref == "MRT Yellow" or "สายสีเหลือง" in blob or "Yellow Line" in blob:
        return "mrt-yellow"
    if ref in {"MRT Pink", "IMPACT Link", "MRT Muang Thong Thani"} or "สายสีชมพู" in blob or "เมืองทองธานี" in blob:
        return "mrt-pink"
    if network == "ARL" or "AERA1" in ref or "เชื่อมท่าอากาศยาน" in blob:
        return "arl"
    if ref == "SRT Dark Red Line" or "สีแดงเข้ม" in blob or "Dark Red" in blob:
        return "srt-dark-red"
    if ref == "SRT Light Red Line" or "สีแดงอ่อน" in blob or "Light Red" in blob:
        return "srt-light-red"
    return None


def way_coords(member: dict) -> list[tuple[float, float]]:
    geom = member.get("geometry") or []
    coords = []
    for point in geom:
        lat, lon = point.get("lat"), point.get("lon")
        if lat is None or lon is None:
            continue
        coords.append((float(lat), float(lon)))
    return coords


def stitch(ways: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    segments: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    for coords in ways:
        if len(coords) < 2:
            continue
        if not current:
            current = coords[:]
            continue
        gap_forward = haversine_m(current[-1][0], current[-1][1], coords[0][0], coords[0][1])
        gap_flip = haversine_m(current[-1][0], current[-1][1], coords[-1][0], coords[-1][1])
        if gap_forward <= JOIN_M or gap_flip <= JOIN_M:
            piece = coords if gap_forward <= gap_flip else list(reversed(coords))
            if haversine_m(current[-1][0], current[-1][1], piece[0][0], piece[0][1]) < 1.5:
                current.extend(piece[1:])
            else:
                current.extend(piece)
        else:
            segments.append(current)
            current = coords[:]
    if current:
        segments.append(current)
    return [seg for seg in segments if len(seg) >= 2]


def length_m(segments: list[list[tuple[float, float]]]) -> float:
    total = 0.0
    for seg in segments:
        for (lat1, lon1), (lat2, lon2) in zip(seg, seg[1:]):
            total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def douglas(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    sx, sy = start[1], start[0]
    ex, ey = end[1], end[0]
    dx, dy = ex - sx, ey - sy
    denom = dx * dx + dy * dy
    max_dist = -1.0
    index = 0
    for i in range(1, len(points) - 1):
        px, py = points[i][1], points[i][0]
        if denom == 0:
            dist = (px - sx) ** 2 + (py - sy) ** 2
        else:
            t = ((px - sx) * dx + (py - sy) * dy) / denom
            dist = (px - (sx + t * dx)) ** 2 + (py - (sy + t * dy)) ** 2
        if dist > max_dist:
            max_dist = dist
            index = i
    if max_dist > epsilon * epsilon:
        left = douglas(points[: index + 1], epsilon)
        right = douglas(points[index:], epsilon)
        return left[:-1] + right
    return [start, end]


def simplify(segments: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    cleaned = []
    for seg in segments:
        simple = douglas(seg, SIMPLIFY_DEG)
        rounded = []
        for lat, lon in simple:
            point = (round(lat, 6), round(lon, 6))
            if not rounded or rounded[-1] != point:
                rounded.append(point)
        if len(rounded) >= 2:
            cleaned.append(rounded)
    return cleaned


def mostly_covered(
    segments: list[list[tuple[float, float]]],
    kept: list[list[tuple[float, float]]],
    thresh_m: float = 45.0,
    fraction: float = 0.9,
) -> bool:
    if not kept:
        return False
    sample: list[tuple[float, float]] = []
    for seg in segments:
        if not seg:
            continue
        step = max(1, len(seg) // 40)
        sample.extend(seg[::step])
        sample.append(seg[-1])
    if not sample:
        return False
    near = 0
    for lat, lon in sample:
        if dist_to_lines(lat, lon, kept) <= thresh_m:
            near += 1
    return near / len(sample) >= fraction


def fetch_routes(cache: Path | None) -> list[dict]:
    if cache and cache.exists():
        print(f"using cached routes {cache}", flush=True)
        return json.loads(cache.read_text())["elements"]
    # Geometry is limited to urban metro routes. A second tags-only pass
    # records other rail relations in the bbox so the report can say why
    # they were left out, without downloading long-distance track.
    print("fetching metro route geometry", flush=True)
    geometry = overpass(
        f"""[out:json][timeout:180];
(
  rel["type"="route"]["route"~"^(subway|light_rail|monorail)$"]{bbox_clause()};
  rel["type"="route"]["route"="train"]["network"="ARL"]{bbox_clause()};
  rel["type"="route"]["route"="train"]["ref"~"Red Line"]{bbox_clause()};
);
out geom;
"""
    )
    print("fetching other rail route tags", flush=True)
    others = overpass(
        f"""[out:json][timeout:90];
rel["type"="route"]["route"~"^(subway|light_rail|monorail|train)$"]{bbox_clause()};
out tags;
"""
    )
    have = {el["id"] for el in geometry["elements"]}
    elements = list(geometry["elements"])
    for el in others["elements"]:
        if el.get("id") not in have:
            el["tags_only"] = True
            elements.append(el)
    payload = {"elements": elements}
    if cache:
        cache.write_text(json.dumps(payload))
        print(f"cached {cache}", flush=True)
    return elements


def fetch_nodes(ids: list[int], cache: Path | None) -> dict[int, dict]:
    if cache and cache.exists():
        print(f"using cached nodes {cache}", flush=True)
        elements = json.loads(cache.read_text())["elements"]
        return {el["id"]: el for el in elements if el.get("type") == "node"}
    nodes: dict[int, dict] = {}
    unique = sorted(set(ids))
    print(f"fetching {len(unique)} stop nodes and railway=station nodes", flush=True)
    print("fetching railway=station nodes", flush=True)
    stations = overpass(
        f"""[out:json][timeout:120];
(
  node["railway"="station"]{bbox_clause()};
  node["public_transport"="station"]["station"~"^(subway|light_rail|monorail)$"]{bbox_clause()};
);
out body;
"""
    )
    for el in stations["elements"]:
        if el.get("type") == "node":
            nodes[el["id"]] = el
    chunk = 500
    for start in range(0, len(unique), chunk):
        batch = [i for i in unique[start : start + chunk] if i not in nodes]
        if not batch:
            continue
        id_list = ",".join(str(i) for i in batch)
        print(f"fetching stop nodes {start + 1}–{start + len(batch)}", flush=True)
        payload = overpass(
            f"""[out:json][timeout:120];
node(id:{id_list});
out body;
"""
        )
        for el in payload["elements"]:
            if el.get("type") == "node":
                nodes[el["id"]] = el
    if cache:
        cache.write_text(json.dumps({"elements": list(nodes.values())}))
    return nodes


def member_node(member: dict, nodes: dict[int, dict]) -> dict | None:
    node = nodes.get(member.get("ref"))
    if node and "lat" in node and "lon" in node:
        return node
    if "lat" in member and "lon" in member:
        return {
            "type": "node",
            "id": member.get("ref"),
            "lat": member["lat"],
            "lon": member["lon"],
            "tags": (node or {}).get("tags") or {},
        }
    return None


def best_station_node(lat: float, lon: float, line_id: str, nodes: list[dict], name_hint: str) -> dict | None:
    hint = norm_name(name_hint)
    best = None
    best_dist = 120.0
    for node in nodes:
        tags = node.get("tags") or {}
        if not passenger_station(tags):
            continue
        dist = haversine_m(lat, lon, node["lat"], node["lon"])
        if dist > best_dist:
            continue
        codes = codes_in(tags.get("ref"))
        code_ok = code_for_line(codes, line_id) is not None
        en, th = name_en(tags), name_th(tags)
        blob = norm_name(en + th + (tags.get("name") or ""))
        name_ok = bool(hint and blob and (hint in blob or blob in hint))
        if not code_ok and not name_ok:
            continue
        # Prefer a tagged station over a bare stop_position when both match.
        rank = dist - (15 if tags.get("railway") == "station" else 0)
        if best is None or rank < best[0]:
            best = (rank, node)
            best_dist = max(dist, 80.0)
    return None if best is None else best[1]


def route_stops(relation: dict, nodes: dict[int, dict], line_id: str, station_nodes: list[dict]) -> list[dict]:
    members = stop_members(relation)
    stops = []
    for member in members:
        node = member_node(member, nodes)
        if not node:
            continue
        tags = node.get("tags") or {}
        if not passenger_station(tags):
            continue
        lat, lon = float(node["lat"]), float(node["lon"])
        en, th = name_en(tags), name_th(tags)
        codes = codes_in(tags.get("ref"))
        code = code_for_line(codes, line_id)
        richer = best_station_node(lat, lon, line_id, station_nodes, en or th or tags.get("name") or "")
        if richer:
            rt = richer.get("tags") or {}
            en = en or name_en(rt)
            th = th or name_th(rt)
            if not code:
                code = code_for_line(codes_in(rt.get("ref")), line_id)
            # Keep the route stop coordinate. It is the stop_position on the
            # operating route. The station node is only a name/code source
            # unless the route node itself has no coordinate, which it does.
        if not en and not th:
            continue
        stops.append({
            "osm_id": node.get("id"),
            "lat": round(lat, 6),
            "lng": round(lon, 6),
            "name_en": en,
            "name_th": th,
            "code": code,
            "line_id": line_id,
        })
    return stops


def dedupe_line_stops(stops: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for stop in stops:
        match = None
        for prev in kept:
            same_code = stop["code"] and stop["code"] == prev["code"]
            same_name = norm_name(stop["name_en"] or stop["name_th"]) and norm_name(
                stop["name_en"] or stop["name_th"]
            ) == norm_name(prev["name_en"] or prev["name_th"])
            close = haversine_m(stop["lat"], stop["lng"], prev["lat"], prev["lng"]) < 180
            if same_code or (same_name and close):
                match = prev
                break
        if match is None:
            kept.append(dict(stop))
            continue
        if stop["code"] and not match["code"]:
            match["code"] = stop["code"]
        if len(stop["name_en"]) > len(match["name_en"]):
            match["name_en"] = stop["name_en"]
        if len(stop["name_th"]) > len(match["name_th"]):
            match["name_th"] = stop["name_th"]
    return kept


def add_stations_on_line(line_id: str, segments: list, stops: list[dict], station_nodes: list[dict]) -> list[dict]:
    extra = []
    for node in station_nodes:
        tags = node.get("tags") or {}
        if not passenger_station(tags):
            continue
        code = code_for_line(codes_in(tags.get("ref")), line_id)
        if not code:
            continue
        lat, lon = float(node["lat"]), float(node["lon"])
        if dist_to_lines(lat, lon, segments) > NEAR_LINE_M:
            continue
        if any(
            (s["code"] == code) or haversine_m(lat, lon, s["lat"], s["lng"]) < 80
            for s in stops
        ):
            # Fill a missing code on the nearby route stop.
            for stop in stops:
                if stop["code"]:
                    continue
                if haversine_m(lat, lon, stop["lat"], stop["lng"]) < 80:
                    stop["code"] = code
                    stop["name_en"] = stop["name_en"] or name_en(tags)
                    stop["name_th"] = stop["name_th"] or name_th(tags)
            continue
        extra.append({
            "osm_id": node.get("id"),
            "lat": round(lat, 6),
            "lng": round(lon, 6),
            "name_en": name_en(tags),
            "name_th": name_th(tags),
            "code": code,
            "line_id": line_id,
        })
    # Several platform nodes share one code. Keep the railway=station node,
    # which is the one we appended only when it was not within 80 m of a stop.
    # Collapse extras that share a code.
    collapsed = []
    for stop in extra:
        prev = next((item for item in collapsed if item["code"] == stop["code"]), None)
        if prev is None:
            collapsed.append(stop)
        elif len(stop["name_en"]) > len(prev["name_en"]):
            prev.update({k: stop[k] for k in ("name_en", "name_th", "lat", "lng", "osm_id")})
    return stops + [s for s in collapsed if s["name_en"] or s["name_th"]]


def cluster_stations(per_line: dict[str, list[dict]]) -> list[dict]:
    items = []
    for line_id, stops in per_line.items():
        for stop in stops:
            items.append(dict(stop))
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i]["line_id"] == items[j]["line_id"]:
                continue
            if haversine_m(items[i]["lat"], items[i]["lng"], items[j]["lat"], items[j]["lng"]) <= MERGE_M:
                union(i, j)
    groups: dict[int, list[dict]] = {}
    for i, item in enumerate(items):
        groups.setdefault(find(i), []).append(item)
    stations = []
    for group in groups.values():
        # One real OSM node represents the complex. Prefer a coded station,
        # then the alphabetically first line so the choice is stable.
        group.sort(key=lambda s: (s["code"] is None, LINE_ORDER.index(s["line_id"]), s["osm_id"] or 0))
        anchor = group[0]
        lines = []
        seen = set()
        for stop in sorted(group, key=lambda s: LINE_ORDER.index(s["line_id"])):
            if stop["line_id"] in seen:
                continue
            seen.add(stop["line_id"])
            meta = CANON[stop["line_id"]]
            lines.append({
                "id": stop["line_id"],
                "name_en": meta["name_en"],
                "name_th": meta["name_th"],
                "short": meta["short"],
                "code": stop["code"],
                "station_name_en": stop["name_en"],
                "station_name_th": stop["name_th"],
                "lat": stop["lat"],
                "lng": stop["lng"],
                "osm_id": f"node/{stop['osm_id']}" if stop["osm_id"] else None,
            })
        codes = [line["code"] for line in lines if line["code"]]
        names = []
        for line in lines:
            if line["station_name_en"] and line["station_name_en"] not in names:
                names.append(line["station_name_en"])
        ident = "-".join(codes).lower() if codes else f"node-{anchor['osm_id']}"
        stations.append({
            "id": ident,
            "name_en": " / ".join(names) if names else (anchor["name_th"] or ident),
            "name_th": next((line["station_name_th"] for line in lines if line["station_name_th"]), ""),
            "names_th": [line["station_name_th"] for line in lines if line["station_name_th"]],
            "lat": anchor["lat"],
            "lng": anchor["lng"],
            "interchange": len(lines) > 1,
            "lines": lines,
            "connections": [],
            "osm_ids": [line["osm_id"] for line in lines if line["osm_id"]],
        })
    stations.sort(key=lambda s: (s["name_en"], s["id"]))
    return stations


def link_interchanges(stations: list[dict]) -> None:
    """Flag interchange pairs that are too far apart to share one marker."""
    for i, left in enumerate(stations):
        for right in stations[i + 1 :]:
            left_lines = {line["id"] for line in left["lines"]}
            right_lines = {line["id"] for line in right["lines"]}
            if left_lines & right_lines:
                continue
            dist = haversine_m(left["lat"], left["lng"], right["lat"], right["lng"])
            same = norm_name(left["name_en"]) and norm_name(left["name_en"]) == norm_name(right["name_en"])
            if dist <= LINK_M or (same and dist <= SAME_NAME_LINK_M):
                left["interchange"] = True
                right["interchange"] = True
                left["connections"].append(connection(right))
                right["connections"].append(connection(left))


def connection(station: dict) -> dict:
    return {
        "id": station["id"],
        "name_en": station["name_en"],
        "lines": [
            {
                "code": line["code"],
                "name_en": line["station_name_en"],
                "name_th": line["station_name_th"],
                "line_id": line["id"],
                "line_short": line["short"],
                "line_name_en": line["name_en"],
            }
            for line in station["lines"]
        ],
    }


def slug_lines(features_stations: list[dict]) -> None:
    seen: dict[str, int] = {}
    for station in features_stations:
        base = station["id"]
        n = seen.get(base, 0)
        seen[base] = n + 1
        if n:
            station["id"] = f"{base}-{n + 1}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lines", type=Path, default=ROOT / "data" / "transit_lines.geojson")
    parser.add_argument("--stations", type=Path, default=ROOT / "data" / "transit_stations.json")
    parser.add_argument("--cache-routes", type=Path, default=None)
    parser.add_argument("--cache-nodes", type=Path, default=None)
    args = parser.parse_args()

    relations = [el for el in fetch_routes(args.cache_routes) if el.get("type") == "relation"]
    print(f"relations {len(relations)}", flush=True)

    classified = []
    skipped = []
    for rel in relations:
        tags = rel.get("tags") or {}
        line_id = classify(tags)
        record = {
            "relation": rel,
            "line_id": line_id,
            "name": tags.get("name") or tags.get("name:en") or "",
            "ref": tags.get("ref") or "",
            "route": tags.get("route") or "",
            "from": tags.get("from") or "",
            "to": tags.get("to") or "",
            "colour": hex_color(tags.get("colour") or tags.get("color")),
        }
        if line_id:
            ways = []
            for member in rel.get("members") or []:
                if member.get("type") == "way" and member.get("role") in {"", "forward"}:
                    coords = way_coords(member)
                    if len(coords) >= 2:
                        ways.append(coords)
            segments = stitch(ways)
            record["segments"] = segments
            record["length_m"] = length_m(segments)
            classified.append(record)
        else:
            # Only mention rail routes inside the metro bbox. The query is
            # already bbox-limited; skip bus-like leftovers and empty names.
            if record["route"] in {"subway", "light_rail", "monorail", "train"}:
                blob = record["name"] + " " + record["ref"]
                if "ขบวนเสริม" in blob:
                    record["skip_reason"] = "short-turn over tracks already drawn as the full Silom line"
                elif "อัตโนมัติ" in blob and "ท่าอากาศยาน" in blob:
                    record["skip_reason"] = "Suvarnabhumi terminal people mover, not the Airport Rail Link"
                elif record.get("relation", {}).get("tags_only"):
                    record["skip_reason"] = "not one of the operating urban lines on this map"
                skipped.append(record)

    chosen: dict[str, list[dict]] = {line_id: [] for line_id in LINE_ORDER}
    for line_id in LINE_ORDER:
        routes = [r for r in classified if r["line_id"] == line_id]
        routes.sort(key=lambda r: r["length_m"], reverse=True)
        for route in routes:
            if route["length_m"] < 200:
                route["skip_reason"] = "geometry shorter than 200 m"
                skipped.append(route)
                continue
            covered = []
            for kept in chosen[line_id]:
                covered.extend(kept["segments"])
            if mostly_covered(route["segments"], covered):
                route["skip_reason"] = "same tracks as a longer relation already kept (reverse direction or short-turn)"
                skipped.append(route)
                continue
            chosen[line_id].append(route)

    stop_ids = []
    for routes in chosen.values():
        for route in routes:
            for member in stop_members(route["relation"]):
                if member.get("ref"):
                    stop_ids.append(member["ref"])
    nodes = fetch_nodes(stop_ids, args.cache_nodes)
    station_nodes = [
        node for node in nodes.values()
        if "lat" in node and "lon" in node and (
            (node.get("tags") or {}).get("railway") == "station"
            or (node.get("tags") or {}).get("public_transport") == "station"
        )
    ]

    per_line: dict[str, list[dict]] = {}
    line_features = []
    summary = []
    for line_id in LINE_ORDER:
        routes = chosen[line_id]
        meta = CANON[line_id]
        segments = []
        for route in routes:
            segments.extend(route["segments"])
        simple = simplify(segments)
        color = next((route["colour"] for route in routes if route["colour"]), meta["color"])
        # Pink's Muang Thong Thani branch is tagged with a second hex. Keep
        # the main line colour so the branch reads as part of MRT Pink.
        if line_id == "mrt-pink":
            main = next((route["colour"] for route in routes if route["ref"] == "MRT Pink" and route["colour"]), None)
            if main:
                color = main
        stops = []
        for route in routes:
            stops.extend(route_stops(route["relation"], nodes, line_id, station_nodes))
        stops = dedupe_line_stops(stops)
        stops = add_stations_on_line(line_id, simple, stops, station_nodes)
        stops = dedupe_line_stops(stops)
        per_line[line_id] = stops
        name_th = next((name_th_of(route["relation"].get("tags") or {}) for route in routes if name_th_of(route["relation"].get("tags") or {})), meta["name_th"])
        feature = {
            "type": "Feature",
            "properties": {
                "id": line_id,
                "name_en": meta["name_en"],
                "name_th": name_th,
                "short": meta["short"],
                "color": color,
                "osm_color": color,
                "operator": (routes[0]["relation"].get("tags") or {}).get("operator") if routes else None,
                "network": (routes[0]["relation"].get("tags") or {}).get("network") if routes else None,
                "osm_relations": [route["relation"]["id"] for route in routes],
                "station_count": len(stops),
                "length_km": round(length_m(simple) / 1000.0, 2),
            },
            "geometry": {
                "type": "LineString" if len(simple) == 1 else "MultiLineString",
                "coordinates": (
                    [[lon, lat] for lat, lon in simple[0]]
                    if len(simple) == 1
                    else [[[lon, lat] for lat, lon in seg] for seg in simple]
                ),
            },
        }
        line_features.append(feature)
        summary.append((line_id, meta["name_en"], len(stops), [s["code"] or s["name_en"] for s in stops], routes))

    stations = cluster_stations(per_line)
    slug_lines(stations)
    link_interchanges(stations)
    interchanges = [s for s in stations if s["interchange"]]

    retrieved = date.today().isoformat()
    lines_doc = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "OpenStreetMap via the Overpass API",
            "license": "ODbL",
            "retrieved": retrieved,
            "endpoint": OVERPASS_ENDPOINTS[0],
            "bbox": {"south": BBOX[0], "west": BBOX[1], "north": BBOX[2], "east": BBOX[3]},
            "note": (
                "Line colours are the OSM colour tag on the operating route relation. "
                "Station coordinates are OSM stop or station nodes. "
                "A gap under 40 m between consecutive way endpoints is joined; longer gaps stay split."
            ),
        },
        "features": line_features,
    }
    stations_doc = {
        "source": "OpenStreetMap via the Overpass API",
        "license": "ODbL",
        "retrieved": retrieved,
        "merge_m": MERGE_M,
        "link_m": LINK_M,
        "station_count": len(stations),
        "interchange_count": len(interchanges),
        "stations": stations,
    }
    args.lines.parent.mkdir(parents=True, exist_ok=True)
    args.lines.write_text(json.dumps(lines_doc, ensure_ascii=False, indent=2) + "\n")
    args.stations.write_text(json.dumps(stations_doc, ensure_ascii=False, indent=2) + "\n")

    print("\n=== lines ===")
    for line_id, name, count, labels, routes in summary:
        rels = ", ".join(
            f"{route['relation']['id']} {route['from']}→{route['to']} ({route['length_m']/1000:.1f} km)"
            for route in routes
        )
        print(f"{name}: {count} stations [{rels}]")
        print("  " + ", ".join(labels))
    print(f"\nunique stations {len(stations)}  interchanges {len(interchanges)}")
    print("\n=== interchanges ===")
    for station in interchanges:
        bits = [
            f"{line['short']} {line['code'] or ''} {line['station_name_en']}".strip()
            for line in station["lines"]
        ]
        print(f"  {station['name_en']}: " + " | ".join(bits))
    print("\n=== skipped route relations ===")
    for route in skipped:
        reason = route.get("skip_reason") or "not an operating line in this map"
        print(f"  {route['relation']['id']} {route['route']} {route['ref']} {route['name']} — {reason}")
    print(f"\nwrote {args.lines} and {args.stations}")


def name_th_of(tags: dict) -> str:
    return name_th(tags)


if __name__ == "__main__":
    main()
