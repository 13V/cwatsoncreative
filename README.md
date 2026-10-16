# Sunday Light

Website for Sunday Light, Charne Watson's photography business in Adelaide (previously cwatson.creative).

Plain HTML, CSS and a little JavaScript with no build step. Upload the folder to any static host
(Netlify, Vercel, Cloudflare Pages, cPanel). Fonts are self-hosted in `fonts/`.

| Page | What's on it |
| --- | --- |
| `index.html` | Hero, why Sunday Light, the six sessions, recent weddings, how it works |
| `portfolio.html` | Wedding gallery plus couples, family and bump & newborn galleries, with a photo viewer |
| `sessions.html` | Each session type, what to wear, questions |
| `about.html` | About Charne and how she works |
| `enquire.html` | Enquiry form |
| `privacy.html`, `404.html` | Privacy notes and the not-found page |

## Adding the photos

Every photo has a fixed file name. Until a file exists, its slot shows an arch placeholder, and a
gallery whose first photo is missing hides itself. Save each photo under its name and it appears.

Export at 2000 px on the long edge (JPG, sRGB). Then run `python3 tools/prepare_photos.py` to
resize anything larger and strip camera and GPS metadata before committing.

### Wedding photos

These are the 23 photos sent over on 16 October.

| File | Size | Photo |
| --- | --- | --- |
| `images/weddings/vineyard-sunset.jpg` | 1333×2000 | Couple on the lawn above the vineyard, pink sunset sky. Home page hero. |
| `images/weddings/silver-car-bouquet.jpg` | 1333×2000 | Bride with bouquet touching the groom’s face, silver vintage car. |
| `images/weddings/bougainvillea-bride.jpg` | 1000×1500 | Bride alone in front of the bougainvillea cottage. |
| `images/weddings/castle-balcony.jpg` | 1333×2000 | Couple on the castle balcony among the greenery. |
| `images/weddings/car-window-smile.jpg` | 1333×2000 | Bride smiling through the silver car window. |
| `images/weddings/grass-overhead.jpg` | 1333×2000 | Couple lying in long grass, shot from above. |
| `images/weddings/bougainvillea-embrace.jpg` | 1333×2000 | Groom kissing the bride’s forehead, bougainvillea and white windows. |
| `images/weddings/arch-mirror.jpg` | 1333×2000 | Bride at the arched mirror putting in earrings. |
| `images/weddings/winery-champagne.jpg` | 2000×1333 | Landscape. Bridal party and champagne spray at the Lloyd Brothers doors. |
| `images/weddings/field-dusk.jpg` | 1333×2000 | Couple sitting in the green paddock at dusk. |
| `images/weddings/jaguar-kiss.jpg` | 1333×2000 | Couple kissing inside the white Jaguar, sun flare. |
| `images/weddings/jaguar-flare.jpg` | 1333×2000 | Couple forehead to forehead by the Jaguar, sun behind. |
| `images/weddings/jaguar-window-kiss.jpg` | 1333×2000 | Groom leaning into the Jaguar window for a kiss, olive tree. |
| `images/weddings/dam-kiss.jpg` | 1333×2000 | Couple kissing by the dam, cloudy sky. |
| `images/weddings/olive-grove-confetti.jpg` | 1500×1000 | Landscape. Petal toss in the olive grove with a dip kiss. |
| `images/weddings/castle-window.jpg` | 1333×2000 | Couple in the arched castle window, cactus in front. |
| `images/weddings/castle-laugh.jpg` | 1333×2000 | Couple laughing in the ivy-covered castle courtyard. |
| `images/weddings/jaguar-veil.jpg` | 1333×2000 | Couple by the Jaguar, veil across the gravel. |
| `images/weddings/gilded-mirror.jpg` | 1333×2000 | Bride in the gold-framed mirror. |
| `images/weddings/bridesmaids-steps.jpg` | 1333×2000 | Bride and bridesmaids in pastels on the steps. |
| `images/weddings/bridesmaids-seated.jpg` | 2000×1333 | Landscape. Bride seated with her bridesmaids. |
| `images/weddings/groomsmen-steps.jpg` | 1333×2000 | Groom and groomsmen on the castle steps. |
| `images/weddings/castle-dip.jpg` | 1333×2000 | Dip in front of the castle towers. |

### Still needed

| File | Size | Photo |
| --- | --- | --- |
| `images/sessions/bump.jpg` | 1333×2000 | A bump photo, portrait. Sessions card and page. |
| `images/sessions/newborn.jpg` | 1333×2000 | A newborn photo, portrait. Sessions card and page. |
| `images/sessions/family.jpg` | 1333×2000 | A family photo, portrait. Sessions card and page. |
| `images/sessions/milestones.jpg` | 1333×2000 | A graduation or 18th photo, portrait. Sessions card and page. |
| `images/about/portrait.jpg` | 1333×2000 | A photo of Charne, ideally with her camera. About page. |

### Optional galleries

`images/portfolio/couples-01.jpg` to `couples-06.jpg`, `family-01.jpg` to `family-08.jpg` and
`bump-newborn-01.jpg` to `bump-newborn-06.jpg`. Any orientation works. Start each gallery at 01:
it stays hidden until its 01 file exists.

## Enquiry form

The form posts JSON to the webhook in the `data-endpoint` attribute in `enquire.html`:

```
https://lumenadl.app.n8n.cloud/webhook/sunday-light-enquiry
```

Create that webhook in n8n before launch (a copy of the Lumen contact workflow works). The payload has
`name`, `email`, `phone`, `session`, `date`, `location`, `message`, `heard`, `submitted` and
`source`. A hidden `company` field catches bots and is never sent. If the request fails, the form
keeps what was typed and points people to Instagram.

## Before launch

- [ ] Add the photos above and run `tools/prepare_photos.py`.
- [ ] Create the n8n webhook and send a test enquiry.
- [ ] Once the domain is set, add `<link rel="canonical">`, make `og:image` an absolute URL on every
      page, and add a `sitemap.xml` (and a `Sitemap:` line in `robots.txt`).
- [ ] Instagram links point to @cwatson.creative. Update them if the handle changes.
- [ ] The About page opens with "Hi, I'm Charne". Change it if she would rather not use her first name.
- [ ] Sessions show "Pricing on enquiry". Add prices if she wants them public.
- [ ] Optional: add an email address to the footer and to the form's error message.

This repository is public, so photos committed here are public too.

## Brand

`brand/` holds the logo exploration and decisions: the arch logo, the palette and the type.

| Colour | Hex | Use |
| --- | --- | --- |
| Paper | `#F6F2EA` | page background |
| Limestone | `#ECE6DB` | alternate sections, placeholders |
| Saltbush | `#8B937A` | hills in the logo |
| Paddock | `#C3964F` | the sun, accents |
| Bark | `#5C4D3F` | headings, buttons, footer |
| Ink | `#3F352B` | body text |
| Gulf | `#A7BBC3` | the wave in the logo |

Type: Cormorant Garamond for headings, Jost for text and labels, Marcellus for the name.
