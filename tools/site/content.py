# Content for the Sunday Light site: photo slots, copy, and page data.

# Every photo slot. key -> (path, width, height, alt, note for the README)
# A slot shows its photo once the file exists; until then nothing is shown in its place.
# Width and height are read from the file when there is one; these are the fallback.
W = 'images/weddings/'
PHOTOS = {
 'vineyard-sunset': (W + 'vineyard-sunset.jpg', 1333, 2000, 'Bride and groom forehead to forehead on a lawn above the vines under a pink sunset sky', 'Couple on the lawn above the vineyard, pink sunset sky. Home page hero.'),
 'silver-car-bouquet': (W + 'silver-car-bouquet.jpg', 1333, 2000, 'Bride holding her bouquet and touching the groom’s face beside a silver vintage car', 'Bride with bouquet touching the groom’s face, silver vintage car.'),
 'bougainvillea-bride': (W + 'bougainvillea-bride.jpg', 1000, 1500, 'Bride laughing in front of a cottage covered in pink bougainvillea', 'Bride alone in front of the bougainvillea cottage.'),
 'castle-balcony': (W + 'castle-balcony.jpg', 1333, 2000, 'Couple on a stone balcony wrapped in greenery', 'Couple on the castle balcony among the greenery.'),
 'car-window-smile': (W + 'car-window-smile.jpg', 1333, 2000, 'Bride smiling through the window of a vintage car', 'Bride smiling through the silver car window.'),
 'grass-overhead': (W + 'grass-overhead.jpg', 1333, 2000, 'Bride and groom lying in long grass, photographed from above', 'Couple lying in long grass, shot from above.'),
 'bougainvillea-embrace': (W + 'bougainvillea-embrace.jpg', 1333, 2000, 'Groom kissing the bride’s forehead in front of bougainvillea', 'Groom kissing the bride’s forehead, bougainvillea and white windows.'),
 'arch-mirror': (W + 'arch-mirror.jpg', 1333, 2000, 'Bride putting in her earrings in an arched mirror', 'Bride at the arched mirror putting in earrings.'),
 'winery-champagne': (W + 'winery-champagne.jpg', 2000, 1333, 'Bridal party cheering as the groom sprays champagne outside the Lloyd Brothers winery doors', 'Landscape. Bridal party and champagne spray at the Lloyd Brothers doors.'),
 'field-dusk': (W + 'field-dusk.jpg', 1333, 2000, 'Bride resting against the groom in a green paddock at dusk', 'Couple sitting in the green paddock at dusk.'),
 'jaguar-kiss': (W + 'jaguar-kiss.jpg', 1333, 2000, 'Couple kissing in the back of a white vintage Jaguar as the sun flares through', 'Couple kissing inside the white Jaguar, sun flare.'),
 'jaguar-flare': (W + 'jaguar-flare.jpg', 1333, 2000, 'Bride and groom forehead to forehead beside a white Jaguar, low sun behind them', 'Couple forehead to forehead by the Jaguar, sun behind.'),
 'jaguar-window-kiss': (W + 'jaguar-window-kiss.jpg', 1333, 2000, 'Groom leaning into the car window to kiss the bride under an olive tree', 'Groom leaning into the Jaguar window for a kiss, olive tree.'),
 'dam-kiss': (W + 'dam-kiss.jpg', 1333, 2000, 'Couple kissing beside the dam with the vineyard behind', 'Couple kissing by the dam, cloudy sky.'),
 'olive-grove-confetti': (W + 'olive-grove-confetti.jpg', 1500, 1000, 'Bridal party throwing petals in an olive grove as the groom dips the bride', 'Landscape. Petal toss in the olive grove with a dip kiss.'),
 'castle-window': (W + 'castle-window.jpg', 1333, 2000, 'Couple framed in an arched castle window above the succulents', 'Couple in the arched castle window, cactus in front.'),
 'castle-laugh': (W + 'castle-laugh.jpg', 1333, 2000, 'Couple laughing in a stone castle courtyard covered in ivy', 'Couple laughing in the ivy-covered castle courtyard.'),
 'jaguar-veil': (W + 'jaguar-veil.jpg', 1333, 2000, 'Bride and groom by the Jaguar with her long veil spread across the gravel', 'Couple by the Jaguar, veil across the gravel.'),
 'gilded-mirror': (W + 'gilded-mirror.jpg', 1333, 2000, 'Bride smiling into a gilded mirror before the ceremony', 'Bride in the gold-framed mirror.'),
 'bridesmaids-steps': (W + 'bridesmaids-steps.jpg', 1333, 2000, 'Bride and bridesmaids in pastel gowns on the castle steps', 'Bride and bridesmaids in pastels on the steps.'),
 'bridesmaids-seated': (W + 'bridesmaids-seated.jpg', 2000, 1333, 'Bride seated with her bridesmaids in pastel gowns', 'Landscape. Bride seated with her bridesmaids.'),
 'groomsmen-steps': (W + 'groomsmen-steps.jpg', 1333, 2000, 'Groom and groomsmen in linen suits on the castle steps', 'Groom and groomsmen on the castle steps.'),
 'castle-dip': (W + 'castle-dip.jpg', 1333, 2000, 'Groom dipping the bride in front of the castle towers', 'Dip in front of the castle towers.'),
 # Still to come: one portrait photo for each of these
 'session-maternity': ('images/sessions/maternity.jpg', 1333, 2000, 'Maternity session', 'A maternity photo, portrait. Investment page.'),
 'session-newborn': ('images/sessions/newborn.jpg', 1333, 2000, 'Newborn session at home', 'A newborn photo, portrait. Investment page.'),
 'session-family': ('images/sessions/family.jpg', 1333, 2000, 'Family session', 'A family photo, portrait. Investment page and the Families tile on the home page.'),
}
WEDDING_KEYS = [k for k, v in PHOTOS.items() if v[0].startswith(W)]
assert len(WEDDING_KEYS) == 23

# Extra portfolio galleries. Each one appears once its photos exist.
EXTRA_GALLERIES = [
 ('couples', 'Couples & engagements', 'images/portfolio/couples-{:02d}.jpg', 6, 'Couples or engagement session'),
 ('family', 'Family', 'images/portfolio/family-{:02d}.jpg', 8, 'Family session'),
 ('maternity', 'Maternity', 'images/portfolio/maternity-{:02d}.jpg', 6, 'Maternity session'),
 ('newborn', 'Newborn', 'images/portfolio/newborn-{:02d}.jpg', 6, 'Newborn session'),
]

# Wedding packages, from her package sheet (October 2026). They differ only in hours, so what every package
# includes is listed once. (name, hours of continuous coverage, price)
WEDDING_PACKAGES = [('Basic', 4, '$1,700'), ('Standard', 6, '$2,100'), ('Premium', 8, '$2,500'),
                    ('Deluxe', 10, '$2,900'), ('Ultimate', 12, '$3,300')]
WEDDING_INCLUDES = ['Continuous coverage for the hours you choose', 'A fully edited digital gallery',
                    'Sneak peeks within 24 hours', 'A pre-wedding consultation']
WEDDING_TERMS = ['Your full gallery within three months',
                 'A 25% non-refundable deposit secures your date',
                 'Payment plans available, with the balance due 14 days before the wedding']

# Sessions on the Investment page, with her prices (October 2026). A session without a price shows
# "Pricing on enquiry". `includes` become the rows of the session's spec sheet (SPEC_LABELS). A session gets a photo
# row once its photo exists. Mini sessions ($220) are left off on purpose: they run as limited-time specials.
# `more` is the Weddings row's one action; its count comes from WEDDING_PACKAGES, so it stays right.
NUMBER_WORDS = ('no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve')
LOCATION = 'Your choice of location around Adelaide (travel further out can be quoted)'
GALLERY = 'Every edited image in a professional online gallery'
SESSIONS = [
 dict(id='weddings', name='Weddings', photo='castle-balcony', price='From $1,700',
      includes=['Five packages, from 4 to 12 hours of coverage', 'Sneak peeks within 24 hours', 'A pre-wedding consultation'],
      more=('#wedding-packages', f'See the {NUMBER_WORDS[len(WEDDING_PACKAGES)]} packages'),
      body=['I photograph weddings the way they feel: getting ready, the nerves, the vows, the champagne and the dance floor.',
            'I keep things calm and quiet, step in when you need direction and stay out of the way when you don’t. '
            'I’ll also help you plan the timeline, so your portraits land in the best light of the day.']),
 dict(id='couples', name='Couples, engagements & proposals', short='Couples', photo='jaguar-flare', price='$350',
      includes=['About 45 minutes', GALLERY, LOCATION],
      body=['Just engaged, about to ask, or simply in love. We’ll walk, talk and wander somewhere beautiful as the sun goes down.',
            'Planning a proposal? I’ll stay out of sight nearby and catch the moment you ask.']),
 dict(id='family', name='Family', photo='session-family', price='$400',
      includes=['45 to 60 minutes', GALLERY, 'Up to five people, then $25 for each extra person', LOCATION],
      body=['Beach walks, golden paddocks and gum trees, or a slow afternoon at home.',
            'Kids get to be kids. I’ll do the work of catching the moments in between.']),
 dict(id='maternity', name='Maternity', photo='session-maternity', price='$350',
      includes=['About 45 minutes', GALLERY, LOCATION, 'Maternity and newborn packages available'],
      body=['A calm, unhurried session while you’re still comfortable and the bump is beautifully round.',
            'On the beach, in a paddock or somewhere that matters to you. Partners and big brothers and sisters are very welcome.']),
 dict(id='newborn', name='Newborn', photo='session-newborn', price='$350',
      includes=[GALLERY, 'At your home or an outdoor location', 'Maternity and newborn packages available'],
      body=['Relaxed lifestyle sessions in the first few weeks, while they’re still tiny and sleepy.',
            'No complicated props. Just your baby, your family and the soft light from your own windows.']),
]

STEPS = [
 ('Say hello', 'Tell me who you are, what you’re after and roughly when. I’ll come back with dates and details.'),
 ('Plan it together', 'We’ll choose a spot and a time. For outdoor sessions that usually means the last hour before sunset.'),
 ('The session', 'Relaxed and unrushed. I’ll give you easy prompts, so you’re never left wondering what to do with your hands.'),
 ('Your gallery', 'Your edited photos arrive in a private online gallery, ready to download and share.'),
]

FAQ = [
 ('When is the best time for a session?',
  'For outdoor sessions, the hour before sunset. In summer that’s often from about 7.30pm, and in winter from about 4pm. I’ll suggest a start time when we book.'),
 ('Where do sessions happen?',
  'Anywhere that means something to you around Adelaide: the beach, the hills, a favourite park or your own home. Further out is fine too, with travel quoted up front. If you’re not sure, I’m happy to suggest a few spots.'),
 ('What if the weather turns?',
  'We’ll keep an eye on the forecast together and move to a new date if we need to.'),
 ('How do we get our photos?',
  'In a private online gallery, ready to download and share with family.'),
 ('Can you help us with what to wear?',
  'Yes. Once you’ve booked I’ll send through some ideas, and you’re welcome to send me photos of your options.'),
]

INSTAGRAM = ('@cwatson.creative', 'https://www.instagram.com/cwatson.creative/')
ENDPOINT = 'https://lumenadl.app.n8n.cloud/webhook/sunday-light-enquiry'

# The enquiry form's "Type of session" option for each session, so "Enquire" links can pre-select it.
FORM_SESSION = {'weddings': 'Wedding', 'couples': 'Couples, engagement or proposal', 'family': 'Family',
                'maternity': 'Maternity', 'newborn': 'Newborn'}
FORM_OPTIONS = ['Wedding', 'Couples, engagement or proposal', 'Family', 'Maternity', 'Newborn',
                'Maternity and newborn package', 'Something else']

# Home page. The hero shows its first photo on phones and both, as a matted diptych, on large screens. The photo
# windows show the first photo on phones and every photo, under an arcade of arches, from 861px.
HERO = ('vineyard-sunset', 'jaguar-flare')
HOME_WINDOWS = [('castle-dip', 'castle-window', 'castle-laugh'), ('dam-kiss', 'jaguar-window-kiss')]
HOME_STATEMENT_PHOTO = 'arch-mirror'
HOME_TILE_PHOTO = {'weddings': 'bougainvillea-embrace', 'couples': 'field-dusk'}  # Investment rows use SESSIONS photos
CONTACT_PHOTO = 'silver-car-bouquet'
INTRO = ['Sunday light is low, warm and in no hurry. It’s the light I chase, and it’s how I want your session to feel: '
         'no stiff poses and no rushing, just time together while I look for the moments in between.',
         'I’ll guide you the whole way, from what to wear to where to stand when the sun drops. You bring your people. '
         'I’ll look after the light.']
# Six portraits for the Instagram contact sheet (Home and Kind words), none of them used elsewhere on Home.
INSTAGRAM_STRIP = ['gilded-mirror', 'bougainvillea-bride', 'car-window-smile', 'grass-overhead',
                   'bridesmaids-steps', 'groomsmen-steps']

# Line plans: '|' breaks below 861px only, '/' from 861px only, '//' at every width, '*…*' is the italic phrase.
HERO_TITLE = 'Photographs that feel//like a *Sunday afternoon.*'
STATEMENT_LINE = 'Sunday light|is low,/warm and|*in no hurry.*'      # her first sentence (asserted below)
CLOSING = {
    'index': 'You bring|your people.//*I’ll look after|the light.*',  # the end of INTRO[1] (asserted below)
    'gallery': 'Your day,//*in this light.*',                        # NEW, for the owner's sign-off
    'investment': 'Let’s plan//*your session.*',                     # NEW
    'kind-words': 'Let’s plan//*something lovely.*',                 # NEW (spec §6.3's fallback; Contact's h1, but Contact has no closing)
}
CLOSING_LEAD = 'Tell me a little about what you’re planning. I’ll get back to you with availability and pricing.'

# Gallery chapters: (id, title, line, keys); the first key is the chapter's cover. All 23 wedding photos, once each.
GALLERY_CHAPTERS = [
    ('getting-ready', 'Getting ready', 'Mirrors, earrings and the last quiet minutes.',
     ['gilded-mirror', 'arch-mirror', 'bougainvillea-bride', 'car-window-smile']),
    ('your-people', 'Your people', 'Your favourite people, the petals and the champagne.',
     ['bridesmaids-steps', 'groomsmen-steps', 'bridesmaids-seated', 'winery-champagne', 'olive-grove-confetti']),
    ('the-two-of-you', 'The two of you', 'Stone walls, bougainvillea and a minute to yourselves.',
     ['castle-window', 'castle-laugh', 'castle-dip', 'castle-balcony', 'bougainvillea-embrace',
      'silver-car-bouquet', 'jaguar-window-kiss']),
    ('golden-hour', 'Golden hour', 'The hour before sunset, when the light goes low and warm.',
     ['vineyard-sunset', 'dam-kiss', 'jaguar-veil', 'jaguar-flare', 'jaguar-kiss', 'field-dusk', 'grass-overhead']),
]

# Kind words. Until real reviews arrive this stays empty and KIND_WORDS_ARE_PLACEHOLDERS stays True: no review text,
# name or attribution reaches any page, the Kind words page shows an honest holding state (and is kept out of search),
# and the other pages show no reviews at all. Real entries are dicts, for example
#   dict(names='Sophie & Tom', session='Wedding', words='…', pull=None, photo=None, photo_is_theirs=False,
#        place=None, season=None, feature=False)
# `pull` (an italic phrase) must be an exact part of `words`; a `photo` may only sit beside a review when
# photo_is_theirs is True, meaning the photo is of the people who wrote it.
KIND_WORDS_ARE_PLACEHOLDERS = True
KIND_WORDS = []
KIND_WORDS_HOLDING_PHOTO = 'jaguar-kiss'

# Investment page
INVESTMENT_HERO = 'jaguar-veil'
# Old sessions.html anchors (it redirects here, keeping the fragment): old id -> the session it became. #milestones
# (graduations, 18ths, birthdays) was dropped in ed55ac9, so it has no section and lands at the top of the page.
OLD_ANCHORS = {'bump': 'maternity'}
INVESTMENT_INTRO = ['These are the photos you’ll frame, share and come back to for years, so every session is planned around '
                    'the best light of the day and the people in it.',
                    'Every session includes help choosing the spot and the time, ideas for what to wear, and your edited '
                    'photos in a private online gallery, ready to download and share.']
# Spec-sheet row labels for each session include (every include becomes a row, in order).
SPEC_LABELS = {'Five packages, from 4 to 12 hours of coverage': 'Coverage', 'Sneak peeks within 24 hours': 'Previews',
               'A pre-wedding consultation': 'Before the day', 'About 45 minutes': 'Time', '45 to 60 minutes': 'Time',
               'Up to five people, then $25 for each extra person': 'Who', LOCATION: 'Where',
               'At your home or an outdoor location': 'Where', 'Maternity and newborn packages available': 'Packages',
               GALLERY: 'Gallery'}

# Where faces sit in each photo (object-position), read from the photos, so cropped slots keep them in view.
FOCUS = {
    'vineyard-sunset': '55% 40%', 'castle-balcony': '50% 42%', 'jaguar-kiss': '50% 40%',
    'jaguar-flare': '52% 36%', 'dam-kiss': '50% 36%', 'jaguar-veil': '62% 34%',
    'castle-dip': '47% 52%', 'jaguar-window-kiss': '42% 44%', 'olive-grove-confetti': '45% 55%',
    'castle-window': '45% 40%', 'arch-mirror': '62% 36%', 'winery-champagne': '50% 62%',
    'castle-laugh': '52% 46%', 'gilded-mirror': '35% 40%', 'bridesmaids-seated': '50% 35%',
    'bridesmaids-steps': '50% 45%', 'groomsmen-steps': '50% 48%', 'bougainvillea-bride': '55% 30%',
    'bougainvillea-embrace': '50% 25%', 'silver-car-bouquet': '55% 28%', 'car-window-smile': '58% 45%',
    'field-dusk': '55% 42%', 'grass-overhead': '50% 50%',
}
PLACES = {}  # optional, owner-supplied place for a photo (key -> 'Mount Lofty'); empty until she sends them


def plain(plan):
    """A line plan as plain text: the breaks become spaces and the italic marks go."""
    return ' '.join(plan.replace('//', ' ').replace('|', ' ').replace('/', ' ').replace('*', '').split())


def landscape(key):
    _, w, h, _, _ = PHOTOS[key]
    return w > h


CYCLE = ['pair-l', 'solo-r', 'pair-r', 'solo-l']


def rhythm_groups(chapters=None):
    """The gallery's rhythm grid: for each chapter, the photos after its cover grouped into rows, as
    [(type, [keys])]. Each chapter starts one step further round the cycle and odd chapters mirror it, so no two
    neighbouring chapters share a layout. Landscapes pair with a following landscape or run wide."""
    out = []
    for c, (_, _, _, keys) in enumerate(chapters or GALLERY_CHAPTERS):
        mirror, i, rest, groups = c % 2 == 1, c % 4, list(keys[1:]), []
        while rest:
            k = rest.pop(0)
            nxt = rest[0] if rest else None
            if landscape(k):
                if nxt and landscape(nxt):
                    groups.append(('land-pair', [k, rest.pop(0)]))
                else:
                    groups.append(('wide', [k]))
                continue
            slot = CYCLE[i % 4]
            if mirror:
                slot = slot[:-1] + ('r' if slot.endswith('l') else 'l')
            if slot.startswith('pair') and nxt and not landscape(nxt):
                groups.append((slot, [k, rest.pop(0)]))
            else:
                groups.append(('solo-' + slot[-1], [k]))
            i += 1
        out.append(groups)
    return out


def rhythm(chapters=None):
    return [[t for t, _ in groups] for groups in rhythm_groups(chapters)]


# ------------------------------------------------------------------ the honesty net (the build fails if any is false)
assert WEDDING_PACKAGES == [('Basic', 4, '$1,700'), ('Standard', 6, '$2,100'), ('Premium', 8, '$2,500'),
                            ('Deluxe', 10, '$2,900'), ('Ultimate', 12, '$3,300')]
assert {s['id']: s['price'] for s in SESSIONS} == {'weddings': 'From $1,700', 'couples': '$350', 'family': '$400',
                                                  'maternity': '$350', 'newborn': '$350'}
assert WEDDING_INCLUDES == ['Continuous coverage for the hours you choose', 'A fully edited digital gallery',
                            'Sneak peeks within 24 hours', 'A pre-wedding consultation']
assert WEDDING_TERMS == ['Your full gallery within three months', 'A 25% non-refundable deposit secures your date',
                         'Payment plans available, with the balance due 14 days before the wedding']
SESSION = {s['id']: s for s in SESSIONS}
assert 'Up to five people, then $25 for each extra person' in SESSION['family']['includes']


def min_price(packages):
    return min((p for _, _, p in packages), key=lambda p: int(p.strip('$').replace(',', '')))


assert 'From ' + min_price(WEDDING_PACKAGES) == SESSION['weddings']['price']           # the closing's facts row
assert sorted(k for c in GALLERY_CHAPTERS for k in c[3]) == sorted(WEDDING_KEYS)        # all 23, once each
assert plain(STATEMENT_LINE) == INTRO[0].split('. ')[0] + '.'
assert INTRO[1].endswith(plain(CLOSING['index']))                                       # her words, unedited
assert plain(HERO_TITLE) == 'Photographs that feel like a Sunday afternoon.'
assert all(PHOTOS[k][1] < PHOTOS[k][2] for k in INSTAGRAM_STRIP)                        # portraits only
assert rhythm() == [['pair-l', 'solo-r'], ['solo-l', 'land-pair', 'wide'],
                    ['pair-r', 'solo-l', 'pair-l', 'solo-r'], ['solo-r', 'pair-r', 'solo-l', 'pair-l']]
assert set(FOCUS) == set(WEDDING_KEYS)
for r in KIND_WORDS:
    assert not r['pull'] or r['pull'] in r['words'], 'a pull phrase must be an exact part of the review'
    assert not r['photo'] or r['photo_is_theirs'], 'a photo may only sit beside the review of the people in it'
for s in SESSIONS:
    assert all(i in SPEC_LABELS for i in s['includes']), 'every include needs a spec-sheet label'
