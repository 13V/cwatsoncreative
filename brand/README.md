# Brand

Rebrand of **cwatson.creative**, Charne Watson's photography business in Adelaide.

**Logo:** the arch, chosen. A window with a low sun over the hills and water.
**Name:** Sunday Light, for now. The website at the repo root uses it.

Private pages, with her photos:

- Naming the arch, five names: https://claude.ai/artifact/GbrFEyztx2S42CQy2MkrkP
- Logo round, where the arch was chosen: https://claude.ai/artifact/9WsbdgTGXhnrfUHy14Wf3F
- First exploration (feed analysis, looks, early names): https://claude.ai/artifact/7nGceHWr3AWDXoHfdLnZRp

## Name shortlist

Each name is in `logos/arch/`, stacked (`<name>.svg`) and on one line (`<name>-line.svg`).

| # | Name | Idea | Domains (16 Oct 2026) |
| --- | --- | --- | --- |
| 1 | **Low Sun** (recommended) | The light she shoots in, and the sun in the arch | lowsun.com.au and lowsunphotography.com unregistered, lowsun.com taken |
| 2 | Sunday Light | Relaxed family afternoons in good light | sundaylightphotography.com unregistered, sundaylight.com taken |
| 3 | Golden Window | The arch as a window full of golden light | goldenwindowphotography.com unregistered, goldenwindow.com taken |
| 4 | C. Watson Photography | Her surname, as her current handle already uses it | cwatsonphotography.com unregistered |
| 5 | Watson & Co. | Her surname as a small studio, with the gold ampersand | watsonandcophotography.com unregistered, watsonandco.com taken |

`.com.au` results are unconfirmed unless listed: the .au registry rate-limited most lookups.
Instagram handles were not checked. Web searches found no photographer using any of the five names.

If she would rather the name point to her, C. Watson Photography is the fallback and uses the same arch.

## The arch

- Mark: an arch outline in Bark, a Paddock sun behind two Saltbush hills, a Gulf wave at the base.
- Name: Marcellus caps, tracked 0.14em. On the website it is outlined (`tools/site/art.py` draws the
  `wordmark-….svg` file), so it looks the same everywhere and loads no font. Connectors (`&`) in Brygada 1918 roman,
  in the text colour: gold is for rules, underlines and art only.
- Small labels: Proza Libre 500 caps, tracked 0.07em ("PHOTOGRAPHY · ADELAIDE").
- Type: Brygada 1918 for headlines, leads and prices (roman, 400–480; italic only for quotes and a few soft
  lines, in the text colour, never gold), Proza Libre 400 for text, buttons and links, in sentence case. Both SIL OFL, self-hosted in `fonts/`.
  They replaced Cormorant Garamond and Jost in October 2026; the exploration files in `logos/` and `src/` still
  show the earlier type.

## Palette

| Colour | Hex | Use |
| --- | --- | --- |
| Paper | `#F6F2EA` | backgrounds |
| Limestone | `#ECE6DB` | inside the arch, avatars |
| Saltbush | `#8B937A` | hills, reversed versions |
| Paddock | `#C3964F` | the sun, connectors, accents |
| Bark | `#5C4D3F` | text and line work |
| Gulf | `#A7BBC3` | the wave |

The far hill uses a Saltbush tint, `#C1C3B2`. All colours are tuned from colours sampled in her Instagram photos.

## Files

- `logos/arch/`: the five names in the arch.
- `logos/photos-with-charne/`: the five logo directions from the logo round, under the earlier working name.
- `logos/*.svg`: the round two names in the coastal badge, kept for reference.
- `src/`: the Python that draws everything. `export_arch.py`, `export_pwc.py` and `export_logos.py` write the
  logo folders. `page.py`, `page3.py` and `page4.py` build the three review pages into `src/site*/`.

The logo text is live and pulls Google Fonts, so open the SVGs in a browser. The final logo gets its
text outlined before it goes into `<img>` tags, print or the website.

The feed photos aren't in this repo because it is public. To rebuild the pages, put them in
`src/site/img/` as `f01.webp` to `f35.webp`, newest first, and copy the ones each page uses into
`src/site3/img/` and `src/site4/img/`.

## Next

1. Pick the name.
2. Search the ASIC business names register and IP Australia trade marks, then register the business name.
3. Register the domain (.com.au needs an ABN) and claim the Instagram handle.
4. Final arch logo files: outlined SVG and PNG, favicon, Instagram avatar, highlight covers, watermark.
5. Build the website.
