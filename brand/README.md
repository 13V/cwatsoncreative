# Brand

Rebrand of **cwatson.creative**, Charne Watson's photography business in Adelaide.

**Status:** round two. The look is chosen; the name is still open.
The full exploration (feed analysis, round one, the five names, mock-ups) is a private page:
https://claude.ai/artifact/7nGceHWr3AWDXoHfdLnZRp

## The look (chosen in round one)

A coastal badge: the name on the ring, gum leaves for the hills over waves for the coast,
and "PHOTOGRAPHY · ADELAIDE" underneath.

| Role | Font |
| --- | --- |
| Name / wordmark | Marcellus, caps, tracked 0.14em |
| Headlines, the ampersand | Cormorant Garamond (italic 500 for `&`) |
| Small labels | Jost 400, caps, tracked |

| Colour | Hex | Use |
| --- | --- | --- |
| Limestone | `#ECE6DB` | backgrounds |
| Paper | `#F6F2EA` | website background |
| Saltbush | `#8B937A` | leaves, reversed badge |
| Paddock | `#C3964F` | the ampersand, accents |
| Bark | `#5C4D3F` | text and line work |
| Gulf | `#A7BBC3` | waves, links |

All six are tuned from colours sampled in her Instagram photos.

## Name shortlist

| | Name | Domain | Handle |
| --- | --- | --- | --- |
| A | Charne Watson | charnewatson.com and .com.au unregistered | @charnewatson.photo |
| **B** | **Charne & Co.** (recommended) | charneandco.com unregistered, .com.au not confirmed | @charneandco |
| C | Saltbush | saltbushphotography.com taken | @saltbush.photo |
| D | Paperbark | paperbarkphotography.com unregistered | @paperbark.photo |
| E | Kin & Coast | kinandcoast.com taken, kinandcoastphotography.com unregistered | @kinandcoast |

Domains were checked by registry (RDAP) lookup on 16 Oct 2026. Confirm with a registrar before buying.
Handles were not checked.

## Files

- `logos/`: wordmark, badge and reversed badge for each name. The text is live and pulls Google
  Fonts, so open these in a browser. Before use in `<img>`, print or the final site, the chosen
  logo gets its text outlined.
- `src/`: the Python that draws the logos (`python3 export_logos.py` writes `logos/`) and builds the
  exploration page (`python3 page.py` writes `src/site/`). The 35 feed photos aren't in this repo,
  so to rebuild the page, put them in `src/site/img/` as `f01.webp` to `f35.webp`, newest first.

## Next

1. Pick the name.
2. Search the ASIC business names register and IP Australia trade marks, then register the business name.
3. Register the domain (.com.au needs an ABN) and claim the Instagram handle.
4. Final logo files: outlined SVG and PNG, favicon, Instagram avatar, watermark.
5. Build the website.
