# Thailand Rental Map

A public rental map for Thailand, starting in Bangkok. The owner posted the first home. Later listings are added by hand. Do not scrape listing portals, and do not scrape sites that require a login.

**Live site:** https://taamyingcharoen96-dot.github.io/thailand-rental-map/

The page is a split list and map (Leaflet, OpenStreetMap). Listings in the same building share one pin with a unit count. Other directory buildings show as small pins once you zoom in. Named buildings within 1 km of The EmQuartier (Phrom Phong, 13.731225, 100.569476) show a hover card with the building name, the street address when OpenStreetMap has one, and a photo. The photo is the first usable public Google Maps place image, saved under `photos/buildings/`. If Maps has no usable photo, the card says “No photo”. A phone tap opens the same card. Buildings outside that sample do not open it. The search box suggests building names in English and Thai, ignoring punctuation and spacing (`ds tower` finds D.S. Tower). You can also filter by monthly rent, bedrooms, and property type. Selecting a unit opens a detail view over the list: a large photo gallery (swipe, arrows, and a fullscreen lightbox) plus the fields stored for that listing. Close it to return to the same list. A compact photo card stays on the map.

The directory covers the Sukhumvit BTS corridor from Nana (E3) through Bearing (E14): every residential building within 2.5 km of Nana, Asok, Phrom Phong, Thong Lo, Ekkamai, Phra Khanong, On Nut, Bang Chak, Punnawithi, Udom Suk, Bang Na, or Bearing. Buildings inside 2.5 km of BTS Ekkamai are also labeled Ekamai, so that zone stays visible along the corridor. Ari (2.5 km around BTS Ari) and Silom–Sathorn (2.5 km around BTS Sala Daeng) are included too. A building in more than one station area is listed once. The rebuilt directory has 7,072 buildings (876 named, 6,196 labeled by street and house number). Names and coordinates are from OpenStreetMap under the [Open Database License](https://www.openstreetmap.org/copyright).

## First listing

D.S. Tower 1 Sukhumvit 33 — 3 bedrooms, 3 bathrooms, 236 sqm condominium in Khlong Tan Nuea, Watthana (Sukhumvit 33 / Phrom Phong).

| Field | Value |
| --- | --- |
| id | `manual-ds-tower-1-suk33-3br-236` |
| Coordinates | 13.7371102, 100.5685765 |
| Photos | `photos/ds-tower-1-sukhumvit-33/01.jpg` through `06.jpg` |
| Building | `osm-way-340330015` (OpenStreetMap: D.S. Towers) |

Rent is not set. Contact is `Ask Taam (manual owner listing)` because no phone or Line was supplied with the manual entry.

## Marque Sukhumvit

Seven condominium ads at Marque Sukhumvit (`osm-way-521687098`, Sukhumvit 39 / Phrom Phong) were copied by hand from public PropertyHub, PropertyScout, and DDproperty pages on 2026-10-28. They are agent listings, not owner-verified, and availability was not confirmed with the owner. Each `contact` is the public phone, Line, or agent name shown on that ad. The pet-friendly unit’s source URL now redirects to the project index and does not show a contact, so that row says `See source listing (no contact shown)`. DDproperty masks the phone and email, so that row keeps the agent name that is visible. Each `source_url` points at the public ad. Four public-gallery photos were saved per unit (`photo_urls`).

| Unit | Rent (THB/mo) | Beds | Size |
| --- | --- | --- | --- |
| 2BR, floor 20 | 185,000 | 2 | 135 sqm |
| 2BR, floor 19 | 130,000 | 2 | 133 sqm |
| 3BR with jacuzzi, floor 25+ | 290,000 | 3 | 191.5 sqm |
| 3BR pet-friendly, floor 20 | 219,000 | 3 | 197 sqm |
| 3BR (BR15903CD) | 230,000 | 3 | 192 sqm |
| 2BR, floor 28 (DDproperty) | 159,000 | 2 | 126 sqm |
| 3BR (PropertyScout 2823962) | 250,000 | 3 | 197 sqm |

Each Marque unit has four photos under `photos/marque-*/`. Searching “Marque” focuses that building. The units share one map pin with a unit count. Open a unit for the large gallery. D.S. Tower 1 stays as its own pin and uses the same detail view (six photos under `photos/ds-tower-1-sukhumvit-33/`).

## The Estelle Phrom Phong

Seven condominium ads at The Estelle Phrom Phong (`osm-way-1037863939`, Sukhumvit 26 / Phrom Phong, Khlong Toei) were copied by hand from public PropertyScout, PropertyHub, and Dot Property pages on 2026-10-28. They are agent listings, not owner-verified, and availability was not confirmed with the owner. Each `contact` is the public Line or phone shown on that ad. Dot Property hides the phone, Line, email, and WhatsApp, so that row says `See source listing (no contact shown)`. Each `source_url` points at the public ad. Four public-gallery interior photos were saved per unit (`photo_urls`). Coordinates are the building pin from OpenStreetMap.

| Unit | Rent (THB/mo) | Beds | Size |
| --- | --- | --- | --- |
| 1BR, floor 30 (PropertyScout 3302373) | 78,000 | 1 | 59.31 sqm |
| 2BR (PropertyScout 2559552; floor not stated) | 175,000 | 2 | 144 sqm |
| 1BR, floor 31 (PropertyScout 2799975) | 84,000 | 1 | 59.31 sqm |
| 2BR, floor 9 (PropertyHub 6084369) | 125,000 | 2 | 93 sqm |
| 2BR (PropertyScout 3441781; floor not stated) | 160,000 | 2 | 99.6 sqm |
| 3BR, floor 24 (Dot Property U6844923R) | 210,000 | 3 | 162 sqm |
| 4BR, floor 13 (PropertyHub LTHC15749) | 350,000 | 4 | 229 sqm |

PropertyScout 2807259 (rented until May 2027) and 2954830 (rented until Jun 2027) were left off. PropertyHub 6196688 redirected to the project index and was absent from the live project page. The 99.6 sqm row is PropertyScout listing 3441781, which the page marks confirmed available a month ago and does not give a floor. Searching “Estelle” focuses the building. The units share one map pin with the unit count.

## Other ฿200,000–฿400,000 ads

Eight more condominium ads in that rent band were copied by hand on 2026-10-28 from public PropertyHub pages (one Marque unit in the band is in the table above, and the Estelle ฿350,000 unit is in the Estelle table). One unit per project. Coordinates are the matching building pin in `data/buildings.json`. They are agent listings, not owner-verified.

| Project | Area | Rent (THB/mo) | Beds | Size |
| --- | --- | --- | --- | --- |
| The Diplomat 39 | Sukhumvit 39 / Phrom Phong | 250,000 | 3 | 237 sqm |
| Le Raffiné Sukhumvit 24 | Sukhumvit 24 / Phrom Phong | 300,000 | 3 | 371 sqm |
| The Crest Sukhumvit 24 | Sukhumvit 24 / Phrom Phong | 200,000 | 3 | 248.37 sqm |
| Belgravia Residences | Sukhumvit 30 / Phrom Phong | 200,000 | 4 | 295 sqm |
| Millennium Residence | Sukhumvit / Asoke | 250,000 | 3 | 260 sqm |
| Khun by Yoo | Thonglor | 275,000 | 3 | 149.5 sqm |
| Tela Thonglor | Thonglor | 300,000 | 3 | 200 sqm |
| Hyde Heritage Thonglor | Thonglor / Ekamai | 220,000 | 3 | 142.42 sqm |

No public ฿200,000–฿400,000 ad was found for a named building in the Ari area. Ritz-Carlton Residences, The Monument Thonglo, GM Height, and Le Raffiné Sukhumvit 39 are not in the building directory, so those seed ads were not added. FazWaz Tela Thonglor U1387992 says available from 15 Mar 2027 and was left off.

## Run locally

GitHub Pages serves the repository root on `main` (`index.html`, `data/`, `photos/`). The same layout works locally:

```bash
python3 -m http.server 47231
```

Open http://127.0.0.1:47231/

## Add a listing

1. Put photos in `photos/<slug>/`.
2. Append one object to `data/listings.json`. `photo_urls` are paths relative to the site root, for example `photos/<slug>/01.jpg`. Set `building_id` to an id from `data/buildings.json`, or `null` if the building is not listed yet.
3. Match `data/listings.schema.json`. Use a stable `id`. Leave `price_thb` and `contact` as `null` when you do not have them.
4. Commit and push to `main`. GitHub Pages publishes that branch from `/`.

## Buildings

`data/buildings.json` is the directory for that corridor plus Ari and Silom–Sathorn. Each record has a stable id, English and Thai names when OpenStreetMap has them, aliases, type (`condo`, `apartment`, or `other`), the station areas it falls in, coordinates, and `source`. Unnamed buildings are included only when OpenStreetMap has a street and house number. Rebuild it with:

```bash
python3 scripts/build_phrom_phong_buildings.py -o data/buildings.json
```

That reads the public Overpass API. Do not copy names from listing portals.

Do not invent listings. Do not scrape Facebook or other sites that require a login. The rows above are hand copies of public ads.

## EmQuartier hover photos

The hover card is only for named buildings within 1 km of The EmQuartier. Photos for that sample are files in `photos/buildings/<building id>.jpg`, linked from each building’s `photo_url`. They come from the first usable public Google Maps place photo (not a map pin, logo, or profile picture). There is no Google login. A building with no nearby Maps place, or no usable photo, keeps the “No photo” placeholder.

This run does not download the rest of the directory. To repeat this sample, or to try another center later:

```bash
python3 scripts/fetch_building_photos.py --lat 13.731225 --lng 100.569476 --radius-m 1000
```

The page still only opens the card for the EmQuartier center in `index.html` (`EMQUARTIER`). Point that constant at the same center if a later run should show cards somewhere else. The script writes `data/building-photo-report.json` with what it saved and what it skipped. It resumes from photos already on disk.

## Sources

`sources.md` and `data/sources.json` list places future listings might come from. Active entries today are the owner’s manual post for D.S. Tower 1 and hand copies of public ads at Marque Sukhumvit, The Estelle Phrom Phong, and the other ฿200,000–฿400,000 projects listed above.
