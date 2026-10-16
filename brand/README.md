# Brand

Rebrand of **cwatson.creative**, Charne Watson's photography business in Adelaide.

**Name:** Photos with Charne.
**Status:** choosing between five logo directions.

Private pages, with her photos:

- Logo round, five directions: https://claude.ai/artifact/9WsbdgTGXhnrfUHy14Wf3F
- Earlier exploration (feed analysis, round one looks, round two names): https://claude.ai/artifact/7nGceHWr3AWDXoHfdLnZRp

## Logo directions

Files are in `logos/photos-with-charne/`: a full logo and a small mark for each.

| # | Direction | Idea | Type |
| --- | --- | --- | --- |
| 1 | The badge | The coastal badge from round one, with the name around the ring | Marcellus, Cormorant italic "with" |
| 2 | The arch | A window with the sun over the hills and water | Marcellus, Cormorant italic "with" |
| 3 | The sun | A golden-hour sun over her name in a soft 70s serif | Fraunces (SOFT 100, WONK 1) |
| 4 | The signature | Her name in script with a gum leaf on the underline | Ephesis as a stand-in for her handwriting, Jost |
| 5 | The rainbow | Four arcs in the palette colours | Jost |

Recommendation: the badge as the logo, with the signature as the watermark on photos.
If it has to be one logo, the sun is the clearest at every size.

## Palette

| Colour | Hex | Use |
| --- | --- | --- |
| Paper | `#F6F2EA` | backgrounds |
| Limestone | `#ECE6DB` | backgrounds, avatars |
| Saltbush | `#8B937A` | leaves, hills, reversed versions |
| Paddock | `#C3964F` | "with", the sun, accents |
| Bark | `#5C4D3F` | text and line work |
| Gulf | `#A7BBC3` | waves, the inner rainbow arc |

All six are tuned from colours sampled in her Instagram photos.

## Name check

- photoswithcharne.com: unregistered (registry lookup, 16 Oct 2026)
- photoswithcharne.com.au: not confirmed, the .au registry rate-limited the lookup
- @photoswithcharne: not checked
- A web search found no business using the name

## Files

- `logos/photos-with-charne/`: the five directions.
- `logos/*.svg`: round two's name shortlist set in the coastal badge, kept for reference.
- `src/`: the Python that draws everything. `python3 export_pwc.py` writes `logos/photos-with-charne/`,
  `python3 export_logos.py` writes the round two files, and `page.py` / `page3.py` build the two
  exploration pages into `src/site/` and `src/site3/`.

The logo text is live and pulls Google Fonts, so open the SVGs in a browser. The chosen logo gets
its text outlined before it goes into `<img>` tags, print or the final site.

The feed photos aren't in this repo because it is public. To rebuild the pages, put them in
`src/site/img/` as `f01.webp` to `f35.webp`, newest first (`page3.py` uses 1, 6, 9, 11 and 19 from
`src/site3/img/`).

## Next

1. Pick a direction, or a pair like the badge with the signature.
2. Charne writes "Charne" 20 or so times with a fine felt-tip; the best one gets vectorised.
3. Search the ASIC business names register and IP Australia trade marks, then register the business name.
4. Register photoswithcharne.com.au (needs an ABN) and the .com, and claim @photoswithcharne.
5. Final files: outlined SVG and PNG, favicon, Instagram avatar, highlight covers, watermark.
6. Build the website.
