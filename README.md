# Thailand Rental Map

A public rental map for Thailand, starting in Bangkok. The owner posted the first home. Later listings are added by hand. Do not scrape listing portals, and do not scrape sites that require a login.

**Live site:** https://taamyingcharoen96-dot.github.io/thailand-rental-map/

The page is a split list and map (Leaflet, OpenStreetMap). Listings in the same building share one pin with a unit count. Other directory buildings show as small pins once you zoom in. Named buildings within 1 km of The EmQuartier (Phrom Phong, 13.731225, 100.569476) show a hover card with the building name, the street address when OpenStreetMap has one, and a photo. The photo is the first usable public Google Maps place image, saved under `photos/buildings/`. If Maps has no usable photo, the card says “No photo”. A phone tap opens the same card. Buildings outside that sample do not open it. The search box suggests building names in English and Thai, ignoring punctuation and spacing (`ds tower` finds D.S. Tower). Filters cover keyword, monthly rent (min and max THB), bedrooms (studio, 1, 2, 3, or 4+), and property type. **More filters** adds pet friendly and furnishing (fully, partly, or unfurnished). The same filters apply to the list and to listing pins, and the result count updates as you change them. Choices are stored in the URL query (`q`, `min`, `max`, `beds`, `type`, `pets`, `furnish`). Reset clears them.

Pet friendly and furnishing match only a value stated in that listing’s title, notes, or source URL. `null` or an omitted field means unknown. Unknown listings stay visible until that filter is set. They are not treated as “no”.

Eleven ads state a pet rule. Marque Sukhumvit 197 sqm (`portal-marque-3br-197-219k-pet`) and The Estelle 162 sqm (`portal-estelle-3br-162-210k-u6844923`) say pet-friendly in the title or notes. Phatsana Garden (`portal-phatsana-garden-4br-345-160k-5001441`) has `pet-friendly` in the source URL. 38 Mansion (`portal-38-mansion-1br-57-25k-6404018`) has `cat-friendly` in the source URL, so it counts as pet friendly. Centurion Park (`portal-centurion-park-1br-53-23k-6368997`) says no pets. Tonson One Residence, Muniq Langsuan, and SCOPE Langsuan in the Lumphini corridor batch below say pet-friendly in the ad text. M Silom in the Chong Nonsi, Saint Louis and Surasak batch below says pet-friendly. The Chao Phraya riverside batch adds a second M Silom unit, 160 sqm (`portal-m-silom-2br-160-119k-6035197`), which says pet-friendly, and Nue Riverest Ratburana (`portal-nue-riverest-ratburana-2br-78-45k-6476049`), which says no pets. The other 276 listings do not state a pet rule. The Marque 197 sqm / ฿250,000 note only distinguishes that unit from the pet-friendly one, so its pet field stays unknown.

One hundred twenty-seven ads say “fully furnished.” Twelve are from the earlier batches: Hyde Heritage Thonglor, Rhythm Sukhumvit 36-38, Hive Sukhumvit 65, The Seed Musee, Royal Kensington Mansion, Phatsana Garden, Siamese Exclusive 42, Tongtip Mansion, The Room Sukhumvit 40, Noble Remix, The Prestige 49, and The Strand Thonglor. Eleven are in the Sukhumvit, Ari, Silom–Sathorn and Bang Na batch below: Sukhumvit Suite, Noble State 39, Baan Siri 24, Aspire Sukhumvit 48, Q House Condo Sukhumvit 79, Ideo Blucove Sukhumvit, City Home Sukhumvit, The Coast Condominium, Ideo Mobi Sukhumvit Eastpoint, The Gallery Bearing, and The Address Sathorn. Twenty are in the Phaya Thai and Ari batch below: FYNN Aree, Onyx Phaholyothin, Life @ Phahon–Ari, Centric Scene Aree 2, Centurion Park, The Fine by Fine Home Ari 4, Aritier Penthouse At Ari, Baan Yoswadi, Harmony Living Paholyothin 11, Intro Phaholyothin-Pradipat, KARA Ari-Rama 6, Suanbua Residence Ari-Ratchakru, The Signature by URBANO, Le Monaco Residence Ari, The Monument Sanampao, Siamese Ratchakru, Park Origin Ratchathewi, The Address Siam-Ratchathewi, CONNER Ratchathewi, and Pyne by Sansiri. Seventeen are in the Lumphini / Rajdamri / Wireless batch: Lumpini Park View, Amanta Lumpini, Saladaeng One, The Sukhothai Residences, The Rajdamri, Noble Ambience Sarasin, The Private Residence Rajdamri, Q Langsuan, Magnolias Ratchadamri Boulevard, Muniq Langsuan, The Residences at Sindhorn Kempinski Hotel Bangkok, 98 Wireless, Klass Langsuan, SCOPE Langsuan, The Nest Ploenchit, Noble Ploenchit, and Ploenchit Terrace. Twenty-two are in the Chong Nonsi, Saint Louis and Surasak batch below: both Ivy Sathorn units, Collezio Sathorn-Pipat, both Quad Silom units, both Noble Revo Silom units, Baan Siri Silom, The Diplomat Sathorn, The Infinity, Klass Silom, Silom Suite, Pikul Place, The Room Sathorn, the Life @ Sathorn 10 2BR, Pearl Garden, M Silom, The Empire Place, Sathorn Prime Residence, The Lofts Silom, Ascott Sathorn Bangkok, and Ashton Silom. Four are at The XXXIX by Sansiri: the 60 sqm, 65.62 sqm, 90 sqm, and 120 sqm units. Forty-one are in the Chao Phraya riverside batch below. The other 160 leave furnishing unknown, including every note that says “furnishing not stated”. 38 Mansion’s URL slug also says fully furnished, but the notes say furnishing was not stated, so that field stays unknown. Khun by Yoo’s “furnished interior renders” describes the gallery, not the unit. Nothing in the copied text states partly furnished or unfurnished. Six listings are studios (`bedrooms` 0): Rhythm Sukhumvit 36-38, Noble Reflex, Ashton Chula–Silom, Life One Wireless, Noble Ploenchit, and Sindhorn Residence.

Not in this filter bar yet: bathrooms, size, distance to BTS/MRT, amenities, zone, and sort.

Selecting a unit opens a detail view over the list: a large photo gallery (swipe, arrows, and a fullscreen lightbox) plus the fields stored for that listing. Close it to return to the same list. A compact photo card stays on the map.

The directory covers the Sukhumvit BTS corridor from Nana (E3) through Bearing (E14): every residential building within 2.5 km of Nana, Asok, Phrom Phong, Thong Lo, Ekkamai, Phra Khanong, On Nut, Bang Chak, Punnawithi, Udom Suk, Bang Na, or Bearing. Buildings inside 2.5 km of BTS Ekkamai are also labeled Ekamai, so that zone stays visible along the corridor. Ari (2.5 km around BTS Ari), Silom–Sathorn (2.5 km around BTS Sala Daeng), and Bang Na (BITEC) (2.5 km around BITEC, OpenStreetMap way/25621160, about 455 m east of BTS Bang Na) are included too. Named residential buildings are also included within 2.5 km of MRT Phra Ram 9, BTS Phaya Thai, BTS Ratchathewi, BTS Chit Lom, BTS Phloen Chit, MRT Lumphini, and BTS Saphan Taksin (Riverside / Charoen Krung). The Chao Phraya riverside is every residential building within 1.5 km of the river centerline (OpenStreetMap relation/227317, แม่น้ำเจ้าพระยา) whose center is inside Bangkok (relation/92277). The buffer is measured in EPSG:32647 and clipped to that boundary, so Nonthaburi, Samut Prakan, and Pathum Thani stay out. Each Bangkok district (khet, admin_level=6) inside the clip is its own zone, labeled Chao Phraya Riverside – that district. A building in more than one area is listed once. The directory has 9,733 buildings. 8,773 are from OpenStreetMap (1,085 named, 7,688 labeled by street and house number). Another 960 condominium projects were copied from public FazWaz project pages because OpenStreetMap had no matching building. Each of those rows uses the project page’s coordinates, sets `source` to `fazwaz`, and keeps the page in `source_url`. A street address is stored only when that page states one. The Bang Na (BITEC) circle sits on top of the Bang Na, Bearing, Udom Suk, and Punnawithi station areas. Names and coordinates are not invented. OpenStreetMap data is under the [Open Database License](https://www.openstreetmap.org/copyright).

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

No public ฿200,000–฿400,000 ad was found for a named building in the Ari area. The Ritz-Carlton Residences At MahaNakhon, 98 Wireless, Saladaeng One, The Monument Thong Lo, and Le Raffiné 39 are in the building directory. GM Height still is not: OpenStreetMap has GM Tower, GM House, and GM Serviced Apartment, and no FazWaz project page titled GM Height turned up in the areas collected here, so that seed ad stays off. FazWaz Tela Thonglor U1387992 says available from 15 Mar 2027 and was left off.

## Thonglor rentals

Twenty-five more condominium and apartment ads within about 1.5 km of BTS Thong Lo were copied on 2026-11-04 from public PropertyHub pages. One unit per project. Each `building_id` is an existing directory pin, and the coordinates are that pin. They are agent listings, not owner-verified. Each `contact` is the Line id and phone on the ad. Four public-gallery photos were saved per unit.

| Project | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- |
| Rhythm Sukhumvit 36-38 | 13,999 | Studio | 24 sqm | LINE @bangkokagency · 0649361416 |
| Hive Sukhumvit 65 | 18,000 | 1 | 40 sqm | LINE @092gbvbz · 0944132653 |
| Condolette Dwell | 20,000 | 1 | 32 sqm | LINE @connexproperty · 0990199900 |
| Siamese Exclusive 42 | 20,000 | 1 | 35 sqm | LINE fryethai · 0897491117 |
| Zenith Place | 20,000 | 1 | 40.57 sqm | LINE @connexproperty · 0990199900 |
| The Room Sukhumvit 40 | 22,000 | 1 | 42 sqm | LINE @375pabiv · 0943905219 |
| Noble Remix | 23,000 | 1 | 44 sqm | LINE @839owdml · 0630795665 |
| Noble Refine | 24,000 | 1 | 33.5 sqm | LINE @connexproperty · 0990199900 |
| 38 Mansion | 25,000 | 1 | 57 sqm | LINE @235dkbrm · 0654731049 |
| The Seed Musee | 35,000 | 2 | 79 sqm | LINE @cutecondo · 0820044299 |
| La Vie En Rose | 45,000 | 2 | 85 sqm | LINE @connexproperty · 0990199900 |
| Acadamia Grand Tower | 45,000 | 2 | 91 sqm | LINE @connexproperty · 0990199900 |
| Baan Suanpetch | 55,000 | 2 | 130 sqm | LINE @connexproperty · 0990199900 |
| Royal Kensington Mansion | 65,000 | 3 | 200 sqm | LINE @bangkokresidential · 0634436327 |
| The Madison | 70,000 | 2 | 115 sqm | LINE @connexproperty · 0990199900 |
| The Alcove 49 | 72,000 | 2 | 110 sqm | LINE @connexproperty · 0990199900 |
| The Strand Thonglor | 72,000 | 1 | 53 sqm | LINE @connexproperty · 0990199900 |
| Premier Condominium | 75,000 | 3 | 228 sqm | LINE @513eqepl · 024607070 |
| Tongtip Mansion | 85,000 | 3 | 245 sqm | LINE @bangkokresidential · 0634436327 |
| Siri Residence | 85,000 | 3 | 141 sqm | LINE @connexproperty · 0990199900 |
| The Prestige 49 | 86,000 | 3 | 210 sqm | LINE @bangkokresidential · 0634436327 |
| Fullerton | 95,000 | 3 | 172 sqm | LINE @eastblue · 0642748883 |
| Kraam Sukhumvit 26 | 110,000 | 2 | 110 sqm | LINE @connexproperty · 0990199900 |
| Vittorio | 140,000 | 2 | 127.43 sqm | LINE @connexproperty · 0990199900 |
| Phatsana Garden | 160,000 | 4 | 345 sqm | LINE @bangkokresidential · 0634436327 |

Ads whose portal pin did not match the directory building were left off, including Greenery Place, Aree Place, Lumpini Suite, and River Place. A PropertyHub ad filed under Grand 39 Tower whose title names D.H. Grand Tower was left off. Khun by Yoo, Tela Thonglor, and Hyde Heritage Thonglor already had ads and were not repeated.

## Sukhumvit, Ari, Silom–Sathorn and Bang Na rentals

Thirty-five more condominium ads were copied on 2026-11-04 from public PropertyHub pages. One unit per project, each at least ฿20,000 a month. Each `building_id` is an existing directory pin, and the coordinates are that pin. They are agent listings, not owner-verified. Each `contact` is the Line id, phone, or WhatsApp on the ad. Four public-gallery photos were saved per unit. Neighborhood is the map station closest to that pin.

| Project | Area | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- | --- |
| Sukhumvit Suite | Nana | 25,000 | 1 | 50 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| Saranjai Mansion | Nana | 27,000 | 1 | 62 sqm | LINE @386ybdef · 0921318369 |
| 15 Sukhumvit Residences | Nana | 30,000 | 1 | 59 sqm | LINE @950iqyse · 0993321768 |
| Ashton Asoke | Asok | 25,000 | 1 | 31 sqm | LINE @910xjpyn · 0950208583 |
| CELES Asoke | Asok | 35,000 | 1 | 35 sqm | LINE @330zzhdy · 0827189785 |
| Las Colinas | Asok | 66,000 | 2 | 145 sqm | LINE @998ynrnr · 0827481996 · WhatsApp 66827481996 |
| NOBLE STATE 39 | Phrom Phong | 25,000 | 1 | 29.81 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| The Address Sukhumvit 28 | Phrom Phong | 52,000 | 2 | 70 sqm | LINE @pfagent · 0962453665 |
| Baan Siri 24 | Phrom Phong | 62,000 | 2 | 98 sqm | LINE @pfagent · 0962453665 |
| The Crest Sukhumvit 34 | Thonglor | 25,000 | 1 | 35 sqm | LINE @688tvdsw · 0948701685 |
| Siri at Sukhumvit | Thonglor | 35,000 | 1 | 52 sqm | LINE @688tvdsw · 0948701685 |
| THE ESSE Sukhumvit 36 | Thonglor | 73,000 | 1 | 72 sqm | LINE @p2nproperty · 0982545162 |
| Noble Reveal | Ekamai | 30,000 | 1 | 47 sqm | LINE @223ifjvn · 0963784472 |
| MODE Sukhumvit 61 | Ekamai | 38,000 | 1 | 57 sqm | LINE @247sbpis · 0612702990 |
| Aspire Sukhumvit 48 | Phra Khanong | 25,000 | 2 | 64.33 sqm | LINE 0809824926 |
| The President Sukhumvit | On Nut | 25,000 | 2 | 49 sqm | LINE @065ikeep · 0617375554 |
| IDEO Mobi Sukhumvit | On Nut | 32,000 | 2 | 55 sqm | LINE @578ovtcs · 0816059481 |
| Q House Condo Sukhumvit 79 | On Nut | 33,000 | 2 | 60 sqm | LINE @pd.residence · 0947404590 |
| Plum Condo Sukhumvit 62 | Bang Chak | 20,000 | 1 | 35 sqm | LINE @600bgvxt · 0944129822 |
| Whizdom Essence Sukhumvit | Punnawithi | 26,000 | 1 | 34 sqm | LINE @539shqpr · 0661384441 |
| IDEO Blucove Sukhumvit | Udom Suk | 20,000 | 2 | 44 sqm | LINE @pfagent · 0962453665 |
| City Home Sukhumvit | Udom Suk | 22,000 | 2 | 75 sqm | LINE @easythaihome · 0855922897 |
| IDEO Mobi Sukhumvit 66 | Udom Suk | 30,000 | 1 | 53 sqm | LINE @046jqoyl · 0633971825 |
| IDEO Mobi Sukhumvit Eastpoint | Bang Na | 25,999 | 2 | 57 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| IDEO O2 | Bang Na | 26,000 | 2 | 53 sqm | LINE @247sbpis · 0612702990 |
| The Coast Condominium | Bang Na | 55,000 | 3 | 92 sqm | LINE happyplace.condo · 0624541459 · WhatsApp 6624541459 |
| The Gallery Bearing | Bearing | 22,000 | 2 | 66 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Niche Mono Sukhumvit - Bearing | Bearing | 22,500 | 1 | 49 sqm | LINE @539shqpr · 0661384441 |
| Very Lasalle | Bearing | 25,000 | 2 | 65 sqm | LINE @319helvo · 0633975106 |
| Noble Reform | Ari | 28,000 | 1 | 47 sqm | LINE @433vejpz · 0963431893 |
| Noble Reflex | Ari | 33,000 | Studio | 42 sqm | LINE @197mqixl · 0620672551 |
| The Address Sathorn | Silom–Sathorn | 25,000 | 1 | 54 sqm | LINE @839owdml · 0630795665 · WhatsApp 66630795665 |
| Sathorn House | Silom–Sathorn | 25,000 | 2 | 55 sqm | LINE @454hhbsx · 0658209826 |
| Supalai Elite Surawong | Silom–Sathorn | 29,000 | 1 | 50 sqm | LINE @046jqoyl · 0633971825 |
| Ashton Chula - Silom | Silom–Sathorn | 35,000 | Studio | 36 sqm | LINE @950iqyse · 0993321768 |

Eleven of these ads say fully furnished: Sukhumvit Suite, Noble State 39, Baan Siri 24, Aspire Sukhumvit 48, Q House Condo Sukhumvit 79, Ideo Blucove Sukhumvit, City Home Sukhumvit, Ideo Mobi Sukhumvit Eastpoint, The Coast Condominium, The Gallery Bearing, and The Address Sathorn. None of these 35 state a pet rule. Noble Reflex and Ashton Chula–Silom are studios. The Gallery Bearing and Niche Mono Sukhumvit - Bearing sit in the Bearing circle; those ads place the projects in Samut Prakan, so city and province follow the ad. An ad filed under Thru Thonglor whose text names True Thonglor was left off. Ads with no public Line, phone, WhatsApp, or email were left off, as were projects whose name and pin did not match a directory building.

## Phaya Thai and Ari rentals

Thirty more condominium ads in Phaya Thai, centered on Ari, were copied on 2026-11-06 from public PropertyHub pages. One unit per project. Ten rent for ฿20,000–฿30,000, ten for ฿30,001–฿79,999, and ten for ฿80,000 or more. The monthly rents run from ฿20,000 to ฿190,000. Twenty-four pins are in the Ari circle. The other six are the nearest Phaya Thai and Ratchathewi projects that had a public ad at ฿80,000 or above: XT Phayathai, Park Origin Ratchathewi, The Address Siam-Ratchathewi, The Line Ratchathewi, CONNER Ratchathewi, and Pyne by Sansiri. Each `building_id` is a directory pin, and the coordinates are that pin. The Monument Sanampao and Siamese Ratchakru were not in the directory; both were added from their public FazWaz project pages. They are agent listings, not owner-verified. Each `contact` is the Line id, phone, or WhatsApp on the ad. Every ad has at least one public-gallery photo; 28 have four. Neighborhood is the map station closest to that pin.

| Project | Area | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- | --- |
| FYNN Aree | Ari | 20,000 | 1 | 26.98 sqm | LINE @iho4335j · 0921806657 |
| Onyx Phaholyothin | Ari | 20,000 | 1 | 40 sqm | LINE p.in · 0882278239 |
| The Line Phahol - Pradipat | Ari | 22,000 | 1 | 34.5 sqm | LINE @condo44 · 0821416464 |
| Centric Scene Aree 2 | Ari | 22,000 | 1 | 39 sqm | LINE @837jruwp · 024304496 |
| The Reserve Phahol-Pradipat | Ari | 22,500 | 1 | 39.24 sqm | LINE @connexproperty · 0990199900 |
| Noble Lite | Ari | 23,000 | 1 | 48 sqm | LINE @condo44 · 0821416464 |
| Centurion Park | Ari | 23,000 | 1 | 53 sqm | LINE @conmatch · 0923437972 |
| The Fine by Fine Home Ari 4 | Ari | 23,000 | 1 | 48.3 sqm | LINE @513eqepl · 024607070 |
| The Crest Phahonyothin 11 | Ari | 25,000 | 2 | 54.6 sqm | LINE @condo65 · 0821416464 |
| Life @ Phahon–Ari | Ari | 28,000 | 2 | 65 sqm | LINE @839owdml · 0630795665 |
| Suanbua Residence Ari-Ratchakru | Ari | 32,000 | 2 | 62.57 sqm | LINE @837jruwp · 024304496 |
| The Signature by URBANO | Ari | 36,000 | 2 | 55 sqm | LINE @837jruwp · 024304496 |
| KARA Ari-Rama 6 | Ari | 38,000 | 2 | 60.61 sqm | LINE @holtop · 0632133317 |
| Noble ReD | Ari | 38,000 | 1 | 54 sqm | LINE @679bhtbt · 0960549296 |
| Harmony Living Paholyothin 11 | Ari | 40,000 | 2 | 96 sqm | LINE lalanakashem · 0849792945 |
| Intro Phaholyothin-Pradipat | Ari | 40,000 | 2 | 92 sqm | LINE @homefinderbangkok · 0957742820 |
| The Vertical Aree | Ari | 40,000 | 2 | 70 sqm | LINE @950iqyse · 0993321768 |
| Villa Ratchakru | Ari | 46,000 | 2 | 147 sqm | LINE @998ynrnr · 0827481996 |
| Baan Yoswadi | Ari | 70,000 | 3 | 210 sqm | LINE @iho4335j · 0921806657 |
| Aritier Penthouse At Ari | Ari | 78,000 | 2 | 110 sqm | LINE @iho4335j · 0921806657 |
| XT Phayathai | Phaya Thai | 80,000 | 3 | 100.5 sqm | LINE @lazudi · 024609389 |
| Park Origin Ratchathewi | Ratchathewi | 80,000 | 3 | 81.86 sqm | LINE @837jruwp · 024304496 |
| The Line Ratchathewi | Ratchathewi | 80,000 | 3 | 120 sqm | LINE @connexproperty · 0990199900 |
| Le Monaco Residence Ari | Ari | 85,000 | 3 | 173 sqm | LINE @homefinderbangkok · 0957742820 |
| The Address Siam-Ratchathewi | Ratchathewi | 85,000 | 2 | 70 sqm | LINE @837jruwp · 024304496 |
| The Monument Sanampao | Ari | 90,000 | 2 | 90.29 sqm | LINE @513eqepl · 024607070 |
| CONNER Ratchathewi | Ratchathewi | 90,000 | 2 | 69 sqm | LINE @sm_th · 0982615588 |
| Phahonyothin Park Condominium | Ari | 95,000 | 3 | 126 sqm | LINE @513eqepl · 024607070 |
| Siamese Ratchakru | Ari | 110,000 | 3 | 160 sqm | LINE @homefinderbangkok · 0957742820 |
| Pyne by Sansiri | Ratchathewi | 190,000 | 3 | 121.75 sqm | LINE @837jruwp · 024304496 |

Twenty of these ads say fully furnished: FYNN Aree, Onyx Phaholyothin, Life @ Phahon–Ari, Centric Scene Aree 2, Centurion Park, The Fine by Fine Home Ari 4, Aritier Penthouse At Ari, Baan Yoswadi, Harmony Living Paholyothin 11, Intro Phaholyothin-Pradipat, KARA Ari-Rama 6, Suanbua Residence Ari-Ratchakru, The Signature by URBANO, Le Monaco Residence Ari, The Monument Sanampao, Siamese Ratchakru, Park Origin Ratchathewi, The Address Siam-Ratchathewi, CONNER Ratchathewi, and Pyne by Sansiri. Centurion Park says no pets and is available from 2026-09-03. The other 29 do not state a pet rule. Life @ Phahon–Ari had two public gallery photos, and Siamese Ratchakru had one. Ads with no public Line, phone, WhatsApp, or email were left off. Noble Reform and Noble Reflex already had ads and were not repeated. A Chewathai Ratchaprarop card priced at ฿145,000 for 35 sqm was left off because that rent does not match the other units in the project.

## Lumphini, Rajdamri and Wireless Road rentals

Thirty more condominium ads along MRT Lumphini, BTS Ratchadamri, BTS Chit Lom, and BTS Phloen Chit (Wireless Road, Langsuan, Sarasin, and Ploenchit) were copied on 2026-11-06 from public PropertyHub pages. One unit per project. Each `building_id` is an existing directory pin, and the coordinates are that pin. They are agent listings, not owner-verified. Each `contact` is the Line id, phone, or WhatsApp on the ad. Four public-gallery photos were saved per unit.

Ten rent for ฿20,000–฿30,000, ten for ฿30,001–฿79,999, and ten for ฿80,000 or more. The rents run from ฿20,000 to ฿650,000. Six are nearest MRT Lumphini (including Saladaeng One and the Saladaeng buildings on the park’s south side). Eleven are on the Rajdamri / Langsuan side. Thirteen are Wireless Road, Chidlom, or Ploenchit (three Wireless, five Chidlom, five Ploenchit). All 30 have a public Line id and a phone; 27 also show WhatsApp. All 30 have four photos.

| Project | Area | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- | --- |
| Lumpini Park View | Lumphini | 22,000 | 1 | 40 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Focus on Saladaeng | Lumphini | 23,000 | 1 | 42 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Amanta Lumpini | Lumphini | 25,000 | 1 | 54 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Saladaeng One | Lumphini | 70,000 | 1 | 57 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| The Sukhothai Residences | Lumphini | 70,000 | 1 | 119 sqm | LINE @leth · 0633695994 · WhatsApp 66633695994 |
| The Royal Saladaeng | Lumphini | 85,000 | 2 | 150 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| The Rajdamri | Rajdamri | 24,000 | 1 | 45 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Noble Ambience Sarasin | Rajdamri | 25,000 | 1 | 49.13 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| The Private Residence Rajdamri | Rajdamri | 30,000 | 1 | 70 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| Sindhorn Residence | Rajdamri | 45,000 | Studio | 33 sqm | LINE @pfagent · 0962453665 |
| Hansar Rajdamri | Rajdamri | 50,000 | 1 | 56 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Q Langsuan | Rajdamri | 60,000 | 2 | 90 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Magnolias Ratchadamri Boulevard | Rajdamri | 80,000 | 2 | 80 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Muniq Langsuan | Rajdamri | 80,000 | 1 | 50 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Baan Ratchadamri | Rajdamri | 220,000 | 4 | 268 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| The Residences at Sindhorn Kempinski Hotel Bangkok | Rajdamri | 250,000 | 2 | 157 sqm | LINE @bridgeestateth · 0994196364 · WhatsApp 66994196364 |
| The Residences at The St. Regis Bangkok | Rajdamri | 600,000 | 3 | 440 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| Life One Wireless | Wireless | 20,000 | Studio | 28 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Noble Above Wireless Ruamrudee | Wireless | 40,000 | 1 | 61 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| 98 Wireless | Wireless | 650,000 | 3 | 263.36 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Klass Langsuan | Chidlom | 22,000 | 1 | 34 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| Na Vara Residence | Chidlom | 37,000 | 1 | 47.24 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| 28 Chidlom | Chidlom | 45,000 | 1 | 44 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Tonson One Residence | Chidlom | 75,000 | 1 | 57 sqm | LINE @bangkokresidential · 0634436327 · WhatsApp 66633583655 |
| SCOPE Langsuan | Chidlom | 160,000 | 1 | 85 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| The Nest Ploenchit | Ploenchit | 21,000 | 1 | 37 sqm | LINE @phenomenal.estate · 0642628787 |
| Noble Ploenchit | Ploenchit | 30,000 | Studio | 44.94 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| Focus Ploenchit | Ploenchit | 35,000 | 2 | 52 sqm | LINE @pfagent · 0962453665 |
| Athenee Residence | Ploenchit | 80,000 | 2 | 99 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Ploenchit Terrace | Ploenchit | 170,000 | 3 | 380 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |

Seventeen of these ads say fully furnished: Lumpini Park View, Amanta Lumpini, Saladaeng One, The Sukhothai Residences, The Rajdamri, Noble Ambience Sarasin, The Private Residence Rajdamri, Q Langsuan, Magnolias Ratchadamri Boulevard, Muniq Langsuan, Sindhorn Kempinski, 98 Wireless, Klass Langsuan, SCOPE Langsuan, The Nest Ploenchit, Noble Ploenchit, and Ploenchit Terrace. Three say pet-friendly: Tonson One Residence, Muniq Langsuan, and SCOPE Langsuan. Life One Wireless, Noble Ploenchit, and Sindhorn Residence are studios. Saladaeng One’s portal pin sits 240 m east of the directory pin; the name matches, and the listing uses the directory coordinates. The Ritz-Carlton Residences at MahaNakhon is in the directory on Narathiwat Road in Silom, outside this corridor, so it was left off. Ads with no public contact, and projects whose name and pin did not match a directory building, were left off.

## Chong Nonsi, Saint Louis and Surasak rentals

Thirty more condominium ads around BTS Chong Nonsi, BTS Saint Louis, and BTS Surasak were copied on 2026-11-08 from public PropertyHub pages. Each `building_id` is an existing directory pin, and the coordinates are that pin. They are agent listings, not owner-verified. Each `contact` is the Line id, phone, or WhatsApp on the ad. A building stays in this batch only when it is within 1 km of one of those three stations and closer to that station than to BTS Sala Daeng or BTS Saphan Taksin.

Ten rent for ฿20,000–฿30,000, ten for ฿30,001–฿79,999, and ten for ฿80,000 or more. The rents run from ฿20,000 to ฿210,000. Thirteen are nearest BTS Chong Nonsi, eleven nearest BTS Saint Louis, and six nearest BTS Surasak. Twenty-six buildings are represented. Ivy Sathorn, Quad Silom, Life @ Sathorn 10, and Noble Revo Silom each have two different units. All 30 have a public Line id and a phone; 25 also show WhatsApp. Twenty-nine have four gallery photos. Ascott Sathorn Bangkok’s ad has one.

| Project | Area | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- | --- |
| Ivy Sathorn | Chong Nonsi | 20,000 | 1 | 35 sqm | LINE @521coash · 0650284348 · WhatsApp 66650284348 |
| ITF Silom Palace | Chong Nonsi | 22,000 | 1 | 56 sqm | LINE @baanlounge · 0628782251 · 0825936597 · WhatsApp 66825936597 |
| Quad Silom | Chong Nonsi | 25,000 | 1 | 45 sqm | LINE @kjcondo · 0934599528 |
| Collezio Sathorn-Pipat | Chong Nonsi | 29,500 | 1 | 42 sqm | LINE @kjcondo · 0934599528 |
| Quad Silom | Chong Nonsi | 33,000 | 2 | 60.89 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Klass Silom Condo | Chong Nonsi | 45,000 | 2 | 70 sqm | LINE @smartmoveagent · 0981466400 · WhatsApp 66981466400 |
| Ivy Sathorn | Chong Nonsi | 47,000 | 2 | 83 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| The Infinity | Chong Nonsi | 55,000 | 2 | 90 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| M Silom | Chong Nonsi | 80,000 | 2 | 84 sqm | LINE @smartmoveagent · 0981466400 · WhatsApp 66981466400 |
| Pearl Garden | Chong Nonsi | 85,000 | 2 | 146 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Ashton Silom | Chong Nonsi | 89,000 | 2 | 75 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| ROMM Convent | Chong Nonsi | 145,000 | 2 | 128 sqm | LINE @nexspace · 0980141559 · WhatsApp 66980141559 |
| The Met | Chong Nonsi | 210,000 | 4 | 404.64 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Life @ Sathorn 10 | Saint Louis | 20,000 | 1 | 40 sqm | LINE eyejidapa2 · 0954506209 · WhatsApp 66954506209 |
| Centric Sathorn - Saint Louis | Saint Louis | 24,000 | 1 | 35 sqm | LINE @319helvo · 0633975106 |
| The Address Sathorn | Saint Louis | 28,000 | 1 | 45 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Life @ Sathorn 10 | Saint Louis | 35,000 | 2 | 65.07 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| Anil Sathorn 12 | Saint Louis | 38,000 | 1 | 47 sqm | LINE @cgestate · 0819194265 · WhatsApp 66819194265 |
| Pikul Place | Saint Louis | 40,000 | 3 | 146 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Silom Suite | Saint Louis | 50,000 | 2 | 80 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Sathorn Prime Residence | Saint Louis | 88,500 | 3 | 185 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Ascott Sathorn Bangkok | Saint Louis | 98,000 | 3 | 197 sqm | LINE @839owdml · 0630795665 · WhatsApp 66630795665 |
| The Empire Place | Saint Louis | 100,000 | 3 | 150 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Sky Villas Sathorn | Saint Louis | 110,000 | 3 | 197.3 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Noble Revo Silom | Surasak | 21,000 | 1 | 33 sqm | LINE @kjcondo · 0934599528 |
| Baan Siri Silom | Surasak | 25,000 | 1 | 45.5 sqm | LINE @kjcondo · 0934599528 |
| The Diplomat Sathorn | Surasak | 30,000 | 1 | 42 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Noble Revo Silom | Surasak | 36,000 | 2 | 65 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| The ROOM Sathorn | Surasak | 36,000 | 1 | 50 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| The Lofts Silom | Surasak | 95,000 | 2 | 107 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |

Twenty-two of these ads say fully furnished. The other eight do not state furnishing: ITF Silom Palace, the Life @ Sathorn 10 1BR, Centric Sathorn - Saint Louis, the new The Address Sathorn 45 sqm unit, Anil Sathorn 12, The Met, Sky Villas Sathorn, and ROMM Convent. None of the thirty states partly furnished or unfurnished. M Silom says pet-friendly. The other 29 do not state a pet rule. The existing The Address Sathorn 54 sqm / ฿25,000 ad and the Sathorn House 55 sqm / ฿25,000 ad were not repeated. Pearl Garden’s portal pin is 226 m from the directory pin, M Silom’s is 261 m, Sathorn Prime Residence’s is 192 m, and ROMM Convent’s is 266 m. The names match, and those listings use the directory coordinates. The Met’s directory name is The Met; the ad names The Met Sathorn, and the project pin is 51 m from the directory pin. The ad text places The Met in Sathon, Thung Maha Mek, which matches the directory address on South Sathorn Road. PropertyHub’s district tag says Bang Rak. The Hudson Sathorn 7 was left off because the ad states ฿90,000 if the room is empty and ฿140,000 with furniture, while the price field says ฿120,000. A The Room Sathorn–St. Louis ad was left off because its portal pin is about 1.7 km south of the directory building. Four Seasons Private Residences Bangkok and The Sukhothai Residences turned up in the Chong Nonsi search and were left off because they sit outside this station corridor. No directory buildings were added.

## The XXXIX by Sansiri rentals

Fourteen condominium ads at The XXXIX by Sansiri (`osm-way-324280501`, Sukhumvit 39 / Phrom Phong, Khlong Tan Nuea, Watthana) were copied on 2026-11-09 from public PropertyHub pages. The building was already in the directory. Each listing uses that pin. The ads’ project pin is 53 m from it. They are current public ads, refreshed 2026-11-09, and availability was not confirmed with the owner. Each `contact` is a Line id, phone, WhatsApp, email, or Facebook name printed on that ad. Each ad has four public-gallery photos.

Seven are 1-bedroom and seven are 2-bedroom. Rents run from ฿44,500 to ฿110,000. All fourteen have a public contact and four photos. Ten name the poster as an agent: EYE (AG) on two ads, Rangrak Estate on two, PropertyScout on five, and Living Home and Condo by Shori Asset Group on one. Four Connex Property ads do not get a role. The profile userType field says OWNER, and the profile text describes a company that advises clients on buying, selling, and renting. The ad does not say that poster owns the unit.

| Unit | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- |
| Floor 24 | 44,500 | 1 | 55 sqm | LINE eyejidapa2 · 0954506209 · WhatsApp 66954506209 |
| Floor 15 | 45,000 | 1 | 59 sqm | LINE eyejidapa2 · 0954506209 · WhatsApp 66954506209 |
| Floor 25 (CX-23944) | 47,000 | 1 | 55 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 · info@connexproperty.co.th · Facebook Connex Property |
| Floor 21 (CX-137144) | 50,000 | 1 | 57 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 · info@connexproperty.co.th · Facebook Connex Property |
| Floor 12A (CP-11627) | 55,000 | 1 | 55 sqm | LINE @accessliving · LINE @rangrak · 0945649169 · 0935245593 · WhatsApp 66935245593 |
| Floor 18 (CX-54882) | 58,000 | 1 | 51 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 · info@connexproperty.co.th · Facebook Connex Property |
| Floor 20 | 65,000 | 1 | 60 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Floor 22 | 69,000 | 2 | 67 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Floor 12A (CP-7345) | 70,000 | 2 | 76 sqm | LINE @mastercondo · LINE @rangrak · 0887863955 · 0935245593 · WhatsApp 66935245593 |
| Floor 20 | 75,000 | 2 | 65.62 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Floor 12 | 80,000 | 2 | 109 sqm | LINE @Livinghomecondo · 0647874793 · WhatsApp 66647874793 |
| Floor 24 | 85,000 | 2 | 90 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Floor 14 (CX-137697) | 90,000 | 2 | 80 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 · info@connexproperty.co.th · Facebook Connex Property |
| Floor 29 | 110,000 | 2 | 120 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |

Four of these ads say fully furnished: the 60 sqm, 65.62 sqm, 90 sqm, and 120 sqm units. The other ten do not state furnishing. None of the fourteen states a pet rule. The two ฿44,500 and ฿45,000 ads say the rent includes one parking space and the common fee. Rangrak Estate’s ads list one Line id in the text and another on the contact card, and both are stored. The card’s WhatsApp value is only a country code, so it is not used. 39 by Sansiri is a different directory building and is not in this batch.

PropertyHub listing 4328270 was left off. Its price field says ฿74,000 and the text says ฿75,000, and the room-type line says 1 bedroom while the bedroom count says 2. Ads whose floor field was a range or a placeholder (1x, 20+, 21–50, 15–39) were left off. Same size, price, and floor already shown by another card on the project page was not repeated. PropertyScout’s own pages hide the poster’s phone, Line, and email, so those pages were not copied. Direct requests to DDproperty, FazWaz, Hipflat, and Dot Property were refused, so ads that appeared only there were not copied. No copied ad states that the poster is the unit owner.

## Chao Phraya riverside rentals

One hundred condominium ads in the Chao Phraya Riverside zone were copied on 2026-11-10 from public PropertyHub pages. Each building’s zone label starts with Chao Phraya Riverside. Each `building_id` is a directory pin, and the coordinates are that pin. They are current public ads, and availability was not confirmed with the owner. Each `contact` is a Line id, phone, or WhatsApp printed on that ad. Ads with no public contact were left off. Each ad has four public-gallery photos.

Thirty-three rent for ฿20,000–฿30,000, thirty-three for ฿30,001–฿79,999, and thirty-four for ฿80,000 or more. The rents run from ฿20,000 to ฿250,000. The 100 ads sit in 51 buildings and 12 districts: Khlong San 16, Bang Kho Laem 15, Yan Nawa 15, Bang Rak 13, Sathon 10, Bang Phlat 8, Thon Buri 7, Bang Sue 6, Rat Burana 6, Samphanthawong 2, Bangkok Noi 1, and Phra Nakhon 1. No building has more than three of these ads. All 100 have a public Line id or phone. Seventy-four name the poster as an agent on the public profile. Twenty-six do not get a role: the profile user type says owner while the profile text describes a brokerage, or the profile page does not state a role, and the ad does not say the poster owns the unit. No copied ad states that the poster is the unit owner.

Forty-one of these ads say fully furnished. The other fifty-nine do not state furnishing. Nothing in this batch states partly furnished or unfurnished. M Silom 160 sqm says pet-friendly. Nue Riverest Ratburana says no pets. The other 98 do not state a pet rule.

Two Flexi ads are filed on PropertyHub under Flexi Riverview Charoennakorn. The ad text and the listing pin name Flexi Sathorn - Charoennakorn in Khlong San, which is a different directory building, so those rows use that pin. The Bangkok Sathorn ad is filed under The Bangkok Sathorn - Taksin. The text says The Bangkok Sathorn, about 50 m from BTS Surasak, so that row uses the Surasak directory pin. Banyan Tree rows use the FazWaz directory pin whose name matches the ad. An August Charoenkrung 80 page whose text is a sale at ฿1,580,000, an Origin Plug & Play Sirindhorn Station card whose rent field says ฿3,290,000 for 25.74 sqm while the text does not state that rent, and a Chateau In Town Pinklao card whose text is a unit at The Line Ratchathewi were left off. Ads whose text named a different project, and same-size same-floor reposts, were not repeated.

| Project | District | Rent (THB/mo) | Beds | Size | Contact |
| --- | --- | --- | --- | --- | --- |
| Bangkok Feliz Sathorn-Taksin | Khlong San | 20,000 | 2 | 47 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Bangkok Feliz Sathorn-Taksin | Khlong San | 25,000 | 2 | 47 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Banyan Tree Residences Riverside Bangkok | Khlong San | 65,000 | 1 | 70 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Banyan Tree Residences Riverside Bangkok | Khlong San | 70,000 | 1 | 70 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Banyan Tree Residences Riverside Bangkok | Khlong San | 190,000 | 2 | 178.34 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Flexi Sathorn - Charoennakorn | Khlong San | 24,000 | 1 | 34 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Flexi Sathorn - Charoennakorn | Khlong San | 26,000 | 1 | 32 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| FLO by Sansiri | Khlong San | 32,000 | 2 | 48 sqm | LINE off_ro · 0859737217 · WhatsApp 66859737217 |
| FLO by Sansiri | Khlong San | 38,000 | 2 | 64 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Magnolias Waterfront Residences | Khlong San | 90,000 | 2 | 102 sqm | LINE @jennyproperties · 0961941966 · WhatsApp 66961941966 |
| Magnolias Waterfront Residences | Khlong San | 110,000 | 2 | 102 sqm | LINE @755pqudx · 0944126961 |
| River House Condominium | Khlong San | 80,000 | 3 | 220 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| Saichol Mansion | Khlong San | 85,000 | 4 | 339 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Saichol Mansion | Khlong San | 95,000 | 4 | 245 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| The River | Khlong San | 85,000 | 2 | 110 sqm | LINE @217jgcbp · 0653619502 · WhatsApp 66638692663 |
| Urbano Absolute Sathon–Taksin | Khlong San | 99,000 | 3 | 165 sqm | LINE @755pqudx · 0944126961 |
| Altitude Symphony Charoenkrung | Bang Kho Laem | 25,000 | 1 | 30.14 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Altitude Symphony Charoenkrung | Bang Kho Laem | 25,000 | 1 | 30 sqm | LINE @688tvdsw · 0948701685 |
| Altitude Symphony Charoenkrung | Bang Kho Laem | 52,000 | 2 | 69 sqm | LINE @319helvo · 0633975106 |
| Canapaya Residences | Bang Kho Laem | 47,000 | 1 | 45 sqm | LINE @645kcgmo · 0634573294 |
| Canapaya Residences | Bang Kho Laem | 78,000 | 2 | 110 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Canapaya Residences | Bang Kho Laem | 225,000 | 4 | 248 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Lumpini Place Rama III-Riverview | Bang Kho Laem | 30,000 | 2 | 88 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Lumpini Place Rama III-Riverview | Bang Kho Laem | 30,000 | 2 | 70 sqm | LINE @condo78 · 0645356369 · WhatsApp 66645356369 |
| Lumpini Place Rama III-Riverview | Bang Kho Laem | 32,000 | 2 | 72 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Menam Residences Condominium | Bang Kho Laem | 80,000 | 3 | 127 sqm | LINE @pfagent · 0962453665 |
| Menam Residences Condominium | Bang Kho Laem | 80,000 | 2 | 99 sqm | LINE @217jgcbp · 0614453194 · WhatsApp 66638692663 |
| One Altitude Charoenkrung | Bang Kho Laem | 120,000 | 3 | 133 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| One Altitude Charoenkrung | Bang Kho Laem | 130,000 | 3 | 132 sqm | LINE @303bkkms · 0819299510 · WhatsApp 66819299510 |
| Rhythm Charoenkrung Pavillion | Bang Kho Laem | 105,000 | 3 | 98 sqm | LINE @217jgcbp · 0614453194 · WhatsApp 66638692663 |
| Rhythm Charoenkrung Pavillion | Bang Kho Laem | 120,000 | 3 | 136 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Baan Lux-Sathon | Yan Nawa | 170,000 | 3 | 370 sqm | LINE @servepm · 0876968665 · WhatsApp 66876968665 |
| Baan Yen Akard | Yan Nawa | 70,000 | 2 | 245 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Baan Yen Akard | Yan Nawa | 80,000 | 2 | 240 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Baan Yen Akard | Yan Nawa | 100,000 | 3 | 300 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| Bridge Sathorn-Narathiwas | Yan Nawa | 20,000 | 1 | 45 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Lumpini Park Riverside Rama 3 | Yan Nawa | 24,000 | 2 | 56 sqm | LINE @kanokestate · 0844279988 |
| Lumpini Park Riverside Rama 3 | Yan Nawa | 25,000 | 2 | 62.02 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Lumpini Park Riverside Rama 3 | Yan Nawa | 37,000 | 3 | 104 sqm | LINE @conmatch · 0923437972 · 0628373269 · 0954920090 · WhatsApp 66628373269 |
| Lumpini Place Water Cliff | Yan Nawa | 20,000 | 2 | 57 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Lumpini Place Water Cliff | Yan Nawa | 50,000 | 3 | 126 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Royal River Place | Yan Nawa | 40,000 | 2 | 139 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Royal River Place | Yan Nawa | 120,000 | 3 | 312.04 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Royal River Place | Yan Nawa | 250,000 | 6 | 539 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Supalai Prima Riva | Yan Nawa | 90,000 | 3 | 255 sqm | LINE @645kcgmo · 0634573294 |
| Supalai Prima Riva | Yan Nawa | 90,000 | 3 | 255.6 sqm | LINE @jennyproperties · 0961941966 · WhatsApp 66961941966 |
| Altitude Samyan-Silom | Bang Rak | 25,000 | 1 | 35 sqm | LINE @280lpyyi · 0968711343 |
| Altitude Samyan-Silom | Bang Rak | 26,000 | 1 | 37 sqm | LINE @280lpyyi · 0968711343 |
| Altitude Samyan-Silom | Bang Rak | 33,000 | 2 | 44 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| Anil Sathorn 12 | Bang Rak | 47,000 | 1 | 46 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Anil Sathorn 12 | Bang Rak | 50,000 | 1 | 46 sqm | LINE @950iqyse · 0993321768 |
| Baan Siri Silom | Bang Rak | 20,000 | 1 | 46 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| Baan Siri Silom | Bang Rak | 32,000 | 1 | 60.7 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| M Silom | Bang Rak | 119,000 | 2 | 160 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Nusa State Tower Condominium | Bang Rak | 120,000 | 2 | 265 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Nusa State Tower Condominium | Bang Rak | 120,000 | 2 | 267 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| State Tower | Bang Rak | 120,000 | 2 | 268 sqm | LINE @condoboy · 021143566 · WhatsApp 66926647892 |
| State Tower | Bang Rak | 120,000 | 2 | 267 sqm | LINE @conmatch · 0923437972 · 0628373269 · 0954920090 · WhatsApp 66628373269 |
| Tanida Residence | Bang Rak | 85,000 | 2 | 87 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Blossom Condo @ Sathorn-Charoenrat | Sathon | 30,000 | 2 | 63 sqm | LINE @535iehwm · 0807911574 |
| Blossom Condo @ Sathorn-Charoenrat | Sathon | 30,000 | 2 | 62 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Rhythm Sathorn | Sathon | 25,000 | 1 | 45 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Rhythm Sathorn | Sathon | 32,000 | 1 | 45 sqm | LINE @easythaihome · 0855922897 |
| Rhythm Sathorn | Sathon | 45,000 | 2 | 66 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Supreme Ville | Sathon | 35,000 | 1 | 71 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Supreme Ville | Sathon | 130,000 | 4 | 301.1 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| The Bangkok Sathorn | Sathon | 80,000 | 2 | 119 sqm | LINE @conmatch · 0923437972 · 0628373269 · 0954920090 · WhatsApp 66628373269 |
| The Issara Sathorn | Sathon | 95,000 | 2 | 110 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| The Issara Sathorn | Sathon | 125,000 | 3 | 188 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Bangkok River Marina | Bang Phlat | 61,000 | 3 | 185 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Bangkok River Marina | Bang Phlat | 70,000 | 2 | 170 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Bangkok River Marina | Bang Phlat | 80,000 | 3 | 181.07 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| Ideo Charan 70 - Riverview | Bang Phlat | 24,000 | 2 | 56 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Ideo Charan 70 - Riverview | Bang Phlat | 25,000 | 2 | 56 sqm | LINE @280lpyyi · 0968711343 |
| Ideo Charan 70 - Riverview | Bang Phlat | 32,000 | 2 | 51 sqm | LINE @280lpyyi · 0968711343 |
| Lumpini Place Rama VIII | Bang Phlat | 28,000 | 2 | 65 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| Thew River Place | Bang Phlat | 47,500 | 2 | 136.59 sqm | LINE @baanlounge · 0628782251 · 0825936597 · WhatsApp 66825936597 |
| 333 Riverside | Bang Sue | 22,000 | 1 | 46 sqm | LINE @330zzhdy · 0827189785 |
| 333 Riverside | Bang Sue | 27,000 | 1 | 45 sqm | LINE @454hhbsx · 0658209826 |
| 333 Riverside | Bang Sue | 50,000 | 2 | 94 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Chapter One Flow Bangpo | Bang Sue | 27,000 | 2 | 66 sqm | LINE off_ro · 0859737217 · WhatsApp 66859737217 |
| Chapter One Flow Bangpo | Bang Sue | 35,000 | 2 | 65.73 sqm | LINE @holtop · 0632133317 · 0979211009 · WhatsApp 66632133317 |
| Chapter One Shine Bangpo | Bang Sue | 35,000 | 2 | 57 sqm | LINE @condopremium · 0633282456 |
| Na Reva Charoennakhon | Thon Buri | 20,000 | 1 | 33.3 sqm | LINE @lazudi · 024609389 · WhatsApp 66959242968 |
| Na Reva Charoennakhon | Thon Buri | 22,000 | 1 | 38 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Na Reva Charoennakhon | Thon Buri | 35,000 | 1 | 55 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Niche Mono Charoen Nakorn | Thon Buri | 20,000 | 1 | 50 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Niche Mono Charoen Nakorn | Thon Buri | 32,000 | 2 | 60 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Supalai River Resort | Thon Buri | 32,000 | 2 | 115 sqm | LINE @454hhbsx · 0658209826 |
| Supalai River Resort | Thon Buri | 120,000 | 3 | 253 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Chapter One Modern Dutch Rat Burana 33 | Rat Burana | 20,000 | 2 | 59 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Chapter One Modern Dutch Rat Burana 33 | Rat Burana | 25,000 | 2 | 60 sqm | LINE @jennyproperties · 0961941966 · WhatsApp 66961941966 |
| Garden Court | Rat Burana | 25,000 | 1 | 81 sqm | LINE @condo42 · 0821416464 · WhatsApp 66652936444 |
| Ivy River | Rat Burana | 33,000 | 2 | 114 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Ivy River | Rat Burana | 35,000 | 2 | 100 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| Nue Riverest Ratburana | Rat Burana | 45,000 | 2 | 78 sqm | LINE @jennyproperties · 0961941966 · WhatsApp 66961941966 |
| Si Phraya River View | Samphanthawong | 29,500 | 1 | 64 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |
| Si Phraya River View | Samphanthawong | 35,000 | 2 | 64 sqm | LINE @513eqepl · 024607070 · WhatsApp 66985629903 |
| dBURA Pran Nok | Bangkok Noi | 20,000 | 2 | 68 sqm | LINE @837jruwp · 024304496 · WhatsApp 66935578313 |
| The 8 Collection | Phra Nakhon | 28,000 | 2 | 44.5 sqm | LINE @connexproperty · 0990199900 · WhatsApp 66990199900 |

## Run locally

GitHub Pages serves the repository root on `main` (`index.html`, `data/`, `photos/`). The same layout works locally:

```bash
python3 -m http.server 47231
```

Open http://127.0.0.1:47231/

## Add a listing

1. Put photos in `photos/<slug>/`.
2. Append one object to `data/listings.json`. `photo_urls` are paths relative to the site root, for example `photos/<slug>/01.jpg`. Set `building_id` to an id from `data/buildings.json`, or `null` if the building is not listed yet.
3. Match `data/listings.schema.json`. Use a stable `id`. Leave `price_thb` and `contact` as `null` when you do not have them. `pet_friendly` and `furnishing` are optional. Set `pet_friendly` to `true` or `false`, or `furnishing` to `fully`, `partly`, or `unfurnished`, only when the listing text says so. Otherwise omit the field or use `null`.
4. Commit and push to `main`. GitHub Pages publishes that branch from `/`.

## Buildings

`data/buildings.json` is the directory for that corridor plus Ari, Silom–Sathorn, Bang Na (BITEC), Phra Ram 9, Phaya Thai, Ratchathewi, Chit Lom, Phloen Chit, Lumphini, Riverside (Saphan Taksin), and the Chao Phraya riverside inside Bangkok. Each record has a stable id, English and Thai names when the source has them, aliases, type (`condo`, `apartment`, or `other`), the areas it falls in, coordinates, and `source`. OpenStreetMap rows use `source` `openstreetmap`. Condominium projects that OpenStreetMap does not already name use `source` `fazwaz` and a `source_url`. Unnamed OpenStreetMap buildings are included only when OpenStreetMap has a street and house number. Rebuild the station radii with:

```bash
python3 scripts/build_phrom_phong_buildings.py -o data/buildings.json
```

That reads the public Overpass API. Do not copy names from listing portals. The Chao Phraya zone is rebuilt with `python3 scripts/build_chao_phraya_zone.py`, which buffers relation/227317 by 1.5 km in EPSG:32647, clips the buffer to Bangkok relation/92277, and copies condominium projects from public FazWaz project pages only when that page’s coordinate falls inside the clip.

Do not invent listings. Do not scrape Facebook or other sites that require a login. The rows above are hand copies of public ads.

## EmQuartier hover photos

The hover card is only for named buildings within 1 km of The EmQuartier. Photos for that sample are files in `photos/buildings/<building id>.jpg`, linked from each building’s `photo_url`. They come from the first usable public Google Maps place photo (not a map pin, logo, or profile picture). There is no Google login. A building with no nearby Maps place, or no usable photo, keeps the “No photo” placeholder.

This run does not download the rest of the directory. To repeat this sample, or to try another center later:

```bash
python3 scripts/fetch_building_photos.py --lat 13.731225 --lng 100.569476 --radius-m 1000
```

The page still only opens the card for the EmQuartier center in `index.html` (`EMQUARTIER`). Point that constant at the same center if a later run should show cards somewhere else. The script writes `data/building-photo-report.json` with what it saved and what it skipped. It resumes from photos already on disk.

## Sources

`sources.md` and `data/sources.json` list places future listings might come from. Active entries today are the owner’s manual post for D.S. Tower 1 and hand copies of public ads at Marque Sukhumvit, The Estelle Phrom Phong, the other ฿200,000–฿400,000 projects, the Thonglor rentals, the Sukhumvit, Ari, Silom–Sathorn and Bang Na rentals, the Phaya Thai and Ari rentals, the Lumphini, Rajdamri and Wireless Road rentals, the Chong Nonsi, Saint Louis and Surasak rentals, The XXXIX by Sansiri rentals, and the Chao Phraya riverside rentals listed above.
