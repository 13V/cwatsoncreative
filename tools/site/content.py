# Content for the Sunday Light site: photo slots, copy, and page data.

# Every photo slot. key -> (path, width, height, alt, note for the README)
# A slot shows its photo once the file exists. Until then it shows the landscape art.
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

# Portfolio order: getting ready, the party, portraits, golden hour
PORTFOLIO_WEDDINGS = ['arch-mirror', 'gilded-mirror', 'bridesmaids-seated', 'bridesmaids-steps', 'groomsmen-steps',
                      'castle-laugh', 'castle-window', 'castle-dip', 'castle-balcony', 'bougainvillea-bride',
                      'bougainvillea-embrace', 'silver-car-bouquet', 'car-window-smile', 'winery-champagne',
                      'olive-grove-confetti', 'dam-kiss', 'jaguar-window-kiss', 'jaguar-veil', 'jaguar-flare',
                      'jaguar-kiss', 'field-dusk', 'grass-overhead', 'vineyard-sunset']
assert sorted(PORTFOLIO_WEDDINGS) == sorted(WEDDING_KEYS)

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
# "Pricing on enquiry". `includes` is the short list under the price. A session's photo card appears once its
# photo exists. Mini sessions ($220) are left off on purpose: they run as limited-time specials.
LOCATION = 'Your choice of location around Adelaide (travel further out can be quoted)'
GALLERY = 'Every edited image in a professional online gallery'
SESSIONS = [
 dict(id='weddings', name='Weddings', photo='bougainvillea-embrace', price='From $1,700',
      includes=['Five packages, from 4 to 12 hours of coverage', 'Sneak peeks within 24 hours', 'A pre-wedding consultation'],
      more=('#wedding-packages', 'See the wedding packages'),
      body=['I photograph weddings the way they feel: getting ready, the nerves, the vows, the champagne and the dance floor.',
            'I keep things calm and quiet, step in when you need direction and stay out of the way when you don’t. '
            'I’ll also help you plan the timeline, so your portraits land in the best light of the day.']),
 dict(id='couples', name='Couples, engagements & proposals', short='Couples', photo='field-dusk', price='$350',
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

# Home page. The hero and the photo windows show their photos side by side on large screens and
# just the first one on phones. Portrait photos keep them sharp on wide screens.
HERO = ('vineyard-sunset', 'jaguar-flare')
HERO_CAPTION = 'Adelaide wedding & family photographer'
HOME_WINDOWS = [('castle-dip', 'castle-window', 'castle-balcony'), ('dam-kiss', 'jaguar-window-kiss')]
INTRO = ['Sunday light is low, warm and in no hurry. It’s the light I chase, and it’s how I want your session to feel: '
         'no stiff poses and no rushing, just time together while I look for the moments in between.',
         'I’ll guide you the whole way, from what to wear to where to stand when the sun drops. You bring your people. '
         'I’ll look after the light.']
TILES = [('Weddings', 'bougainvillea-embrace', 'gallery.html#weddings'),
         ('Couples', 'field-dusk', 'investment.html#couples'),
         ('Families', 'session-family', 'investment.html#family')]
INSTAGRAM_STRIP = ['gilded-mirror', 'bridesmaids-seated', 'car-window-smile', 'grass-overhead', 'winery-champagne',
                   'groomsmen-steps']

# Kind words. Until real reviews arrive this stays empty and KIND_WORDS_ARE_PLACEHOLDERS stays True: no review text,
# name or attribution reaches any page, the Kind words page shows an honest holding state (and is kept out of search),
# and the other pages show no reviews at all. Real entries are (names, session, words, photo key), and a photo may only
# sit beside a review if it is of the people who wrote it.
KIND_WORDS_ARE_PLACEHOLDERS = True
KIND_WORDS = []
KIND_WORDS_HOLDING_PHOTO = 'jaguar-kiss'

# Investment page
INVESTMENT_HERO = ('bridesmaids-steps', 'groomsmen-steps')
INVESTMENT_INTRO = ['These are the photos you’ll frame, share and come back to for years, so every session is planned around '
                    'the best light of the day and the people in it.',
                    'Every session includes help choosing the spot and the time, ideas for what to wear, and your edited '
                    'photos in a private online gallery, ready to download and share.']

# Where to centre photos that get cropped hard.
FOCUS = {
    'winery-champagne': '50% 62%',
    'olive-grove-confetti': '50% 55%',
    'jaguar-flare': '50% 36%',
    'castle-window': '50% 36%',
}
