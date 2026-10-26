# Sunday Light

Website for Sunday Light, Charne Watson's photography business in Adelaide (previously cwatson.creative).

Plain HTML, CSS and a little JavaScript. The pages are generated from `tools/site/` (see Editing the
pages) and the generated HTML is committed, so any static host (Vercel, Netlify, Cloudflare Pages,
cPanel) can serve the folder as it is. Fonts are self-hosted in `fonts/`, each with its licence (SIL OFL).

The site keeps to four tabs, Gallery, Investment, Kind words and Contact, and puts the photos and the
people in them first.

| Page | What's on it |
| --- | --- |
| `index.html` | Full-screen photo, a short intro, photo bands, Weddings / Couples / Families tiles, kind words, Instagram |
| `gallery.html` | Wedding gallery with a photo viewer. Couples, family, maternity and newborn galleries appear once they have photos. |
| `investment.html` | Each session with its price, what it includes and an enquire link; how it works; questions |
| `kind-words.html` | Reviews |
| `contact.html` | Enquiry form. Links from the Investment page arrive with the session already chosen. |
| `privacy.html`, `404.html` | Privacy notes and the not-found page |

The old pages (`portfolio`, `sessions`, `enquire` and `about`) redirect to their replacements on Vercel
(see `vercel.json`).

## The scroll effect

The full-width photo bands hold still while the page slides up over them, then fade to black and white
as they leave the screen. It's all CSS (scroll-driven animations, in `tools/site/css/30-photos-windows.css`),
with no JavaScript. Browsers that don't support scroll-driven animations yet, and devices set to reduce
motion, show the same photos still and in colour.

The photos in the bands are set in `tools/site/content.py`: `HERO` and `HOME_WINDOWS` on the home page,
`INVESTMENT_HERO` on the Investment page. Large screens show two or three side by side; phones show the
first.

## Adding the photos

Every photo has a fixed file name. Until its file exists, a slot shows a soft landscape illustration,
and a gallery only appears once it has photos.

1. Export at 2000 px on the long edge (JPG, sRGB) and save it under its name below.
2. Run `python3 tools/prepare_photos.py` (it needs Pillow: `pip install pillow`). It strips camera and
   GPS details from any photo that has them, makes the WebP copies that phones and smaller screens
   load (320, 480, 800, 1000 and 1200 px wide, plus full size), and rebuilds the pages so the new photos appear.
3. Commit the photos, their `.webp` copies and the rebuilt pages.

### Wedding photos

All 23 are in place, with their WebP copies. They came over on 16 October as 2000 px exports with no
camera or GPS data, so the JPGs are committed as sent.

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
| `images/sessions/maternity.jpg` | 1333×2000 | A maternity photo, portrait. Investment page. |
| `images/sessions/family.jpg` | 1333×2000 | A family photo, portrait. Investment page and the Families tile on the home page. |
| `images/sessions/newborn.jpg` | 1333×2000 | A newborn photo, portrait. Investment page. |

Until they arrive, those sessions show as text cards on the Investment page, and the Families tile shows
the landscape illustration.

### Optional galleries

`images/portfolio/couples-01.jpg` to `couples-06.jpg` (couples and engagements), `family-01.jpg` to
`family-08.jpg`, `maternity-01.jpg` to `maternity-06.jpg` and `newborn-01.jpg` to `newborn-06.jpg`. Any orientation works. Each gallery, and its button
at the top of the Gallery page, appears once it has at least one photo.

## Kind words

There are no real reviews yet, so none are shown anywhere: `KIND_WORDS` in `tools/site/content.py` is empty and
`KIND_WORDS_ARE_PLACEHOLDERS` is `True`. The Kind words page shows an honest holding state (a photo, a short line and
a link to Instagram) and is kept out of search; the other pages show no review section. To add reviews, add entries
to `KIND_WORDS` as `(names, session, words, photo key)`, three to six works best, and only pair a review with a photo
of the people who wrote it. Then set `KIND_WORDS_ARE_PLACEHOLDERS = False` and rebuild; until then every build prints
a reminder.

## Prices

Prices and what each session includes are in `SESSIONS` in `tools/site/content.py` (`price` and `includes`),
and the five wedding packages are in `WEDDING_PACKAGES`, `WEDDING_INCLUDES` and `WEDDING_TERMS`. As of October
2026: weddings from $1,700 (Basic 4 hours $1,700, Standard 6 hours $2,100, Premium 8 hours $2,500, Deluxe 10
hours $2,900, Ultimate 12 hours $3,300); couples, engagements and proposals $350; family $400 (up to five
people, then $25 each); maternity $350; newborn $350. Mini sessions ($220) are limited-time specials, so they
are left off. Change a price there and rebuild.

## Editing the pages

The words, photo slots and galleries are in `tools/site/content.py`, and the page layouts are in
`tools/site/build.py`. Styles and behaviour are written as small numbered parts in `tools/site/css/` and
`tools/site/js/`; the build joins them, in file-name order, into `styles.css` and `main.js`. After changing any of
these, run `python3 tools/site/build.py` to rewrite the HTML, `styles.css`, `main.js`, `favicon.svg` and the wordmark
(`wordmark-<hash>.svg`, named by its content so `vercel.json` can cache it for good).
Don't edit the joined files directly: the next build overwrites them.

## Tests

`tools/tests/` holds browser checks for every page: navigation, the enquiry form (with FormSubmit mocked), prices
and packages, the photo viewer, the phone menu, the photo windows, the motion system, phone layouts at eight
sizes, and the font fallbacks (headings wrap the same before the fonts arrive, and a late font moves nothing). Serve the folder (for example `npx serve -c '{"cleanUrls": false}' .`) and run
`node tools/tests/run.js http://localhost:3000`, or add a name to run one file
(`node tools/tests/run.js http://localhost:3000 investment`). They need Playwright with Chromium.

## Enquiry form

Enquiries are emailed to Charne at cengelbrecht02@gmail.com by [FormSubmit](https://formsubmit.co), a free
form-to-email relay (set by `FORM_TO` in `tools/site/content.py`). With JavaScript, `60-form.js` posts JSON to
`https://formsubmit.co/ajax/<address>`. FormSubmit sends it as a table, with the subject
"New enquiry: {session} from {name}", rows labelled Name, Email, Phone, Session, Date or season, Where, Message and
How they found me (empty answers are left out), and Reply set to the person who wrote. Without JavaScript the form
is a plain post to `https://formsubmit.co/<address>`, and FormSubmit shows its own thank-you page. The hidden `_honey`
field is FormSubmit's bot trap; the script also skips sending when it's filled. If sending fails, the form keeps
what was typed and points people to Instagram.

**Activating it (once).** The first enquiry doesn't arrive: FormSubmit sends an "Activate Form" email to the address
instead, and the form shows its error until the link in that email is clicked. Send one test enquiry from the live
site, click Activate in that email (check spam), then send another test to see a real one arrive. FormSubmit's
emails then offer a random string that can replace the address in `FORM_TO`, so the address isn't in the page
source; swap it in and rebuild.

## Deploying

The Vercel project is connected to this repository, so every push to the default branch goes live by
itself. On `.vercel.app` addresses, `vercel.json` adds an `X-Robots-Tag: noindex` header, so search
engines only index the site once it's on its real domain.

## Before launch

- [x] Add the 23 wedding photos.
- [ ] Add the session photos under "Still needed", then run `tools/prepare_photos.py`.
- [ ] Replace the Kind words placeholders with real reviews (see Kind words).
- [x] Add session prices.
- [x] Add the wedding packages.
- [ ] Activate the enquiry form: send a test enquiry, click Activate in FormSubmit's email, send another.
- [ ] Once the domain is set, add `<link rel="canonical">`, make `og:image` an absolute URL on every
      page, and add a `sitemap.xml` (and a `Sitemap:` line in `robots.txt`).
- [ ] Instagram links point to @cwatson.creative. Update them if the handle changes.
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

Type: Brygada 1918 for headings, leads and prices; Proza Libre for text, buttons, links and the small caps labels
(the only text in caps). The name is Marcellus caps tracked 0.14em, outlined to `wordmark-<hash>.svg` by
`tools/site/art.py`, so no font loads for it. Each font has a metric-matched fallback in
`tools/site/css/00-base.css`, so the page doesn't move when the font arrives.
