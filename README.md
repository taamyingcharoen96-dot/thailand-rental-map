# Thailand Rental Map

A public rental map for Thailand, starting in Bangkok. The owner posts the first home; later listings are added by hand. Nothing here is scraped.

**Live site:** https://taamyingcharoen96-dot.github.io/thailand-rental-map/

The page is a split list and map (Leaflet, OpenStreetMap). Listings in the same building share one pin with a unit count. Other directory buildings show as small pins once you zoom in. The search box suggests building names in English and Thai, ignoring punctuation and spacing (`ds tower` finds D.S. Tower). You can also filter by monthly rent, bedrooms, and property type. Selecting a unit opens its photo card.

The directory covers the Sukhumvit BTS corridor from Nana (E3) through Bearing (E14): every residential building within 2.5 km of Nana, Asok, Phrom Phong, Thong Lo, Ekkamai, Phra Khanong, On Nut, Bang Chak, Punnawithi, Udom Suk, Bang Na, or Bearing. Buildings inside 2.5 km of BTS Ekkamai are also labeled Ekamai, so that zone stays visible along the corridor. Ari (2.5 km around BTS Ari) and Silom–Sathorn (2.5 km around BTS Sala Daeng) are included too. A building in more than one station area is listed once. The rebuilt directory has 7,072 buildings (876 named, 6,196 labeled by street and house number). Names and coordinates are from OpenStreetMap under the [Open Database License](https://www.openstreetmap.org/copyright).

## First listing

D.S. Tower 1 Sukhumvit 33 — 3 bedrooms, 3 bathrooms, 236 sqm condominium in Khlong Tan Nuea, Watthana (Sukhumvit 33 / Phrom Phong).

| Field | Value |
| --- | --- |
| id | `manual-ds-tower-1-suk33-3br-236` |
| Coordinates | 13.7371102, 100.5685765 |
| Photos | `photos/ds-tower-1-sukhumvit-33/01.jpg` through `06.jpg` |
| Building | `osm-way-340330015` (OpenStreetMap: D.S. Towers) |

Rent and contact are not set yet.

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

Do not invent listings. Do not scrape Facebook or other sites that require a login.

## Sources

`sources.md` and `data/sources.json` list places future listings might come from. The only active source today is a manual post from the owner.
