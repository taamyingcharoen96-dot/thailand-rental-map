# Thailand Rental Map

A public rental map for Thailand, starting in Bangkok. The owner posts the first home; later listings are added by hand. Nothing here is scraped.

**Live site:** https://taamyingcharoen96-dot.github.io/thailand-rental-map/

The page is a split list and map (Leaflet, OpenStreetMap). You can filter by search, monthly rent, bedrooms, and property type. Green pins stay in sync with the list. Selecting a listing opens a photo card; when a home has more than one photo, the card steps through them.

## First listing

D.S. Tower 1 Sukhumvit 33 — 3 bedrooms, 3 bathrooms, 236 sqm condominium in Khlong Tan Nuea, Watthana (Sukhumvit 33 / Phrom Phong).

| Field | Value |
| --- | --- |
| id | `manual-ds-tower-1-suk33-3br-236` |
| Coordinates | 13.7371102, 100.5685765 |
| Photos | `photos/ds-tower-1-sukhumvit-33/01.jpg` through `06.jpg` |

Rent and contact are not set yet.

## Run locally

GitHub Pages serves the repository root on `main` (`index.html`, `data/`, `photos/`). The same layout works locally:

```bash
python3 -m http.server 47231
```

Open http://127.0.0.1:47231/

## Add a listing

1. Put photos in `photos/<slug>/`.
2. Append one object to `data/listings.json`. `photo_urls` are paths relative to the site root, for example `photos/<slug>/01.jpg`.
3. Match `data/listings.schema.json`. Use a stable `id`. Leave `price_thb` and `contact` as `null` when you do not have them.
4. Commit and push to `main`. GitHub Pages publishes that branch from `/`.

Do not invent listings. Do not scrape Facebook or other sites that require a login.

## Sources

`sources.md` and `data/sources.json` list places future listings might come from. The only active source today is a manual post from the owner.
