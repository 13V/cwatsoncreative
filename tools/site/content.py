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
 'session-bump': ('images/sessions/bump.jpg', 1333, 2000, 'Maternity session', 'A bump photo, portrait. Sessions page and the home page sessions list.'),
 'session-newborn': ('images/sessions/newborn.jpg', 1333, 2000, 'Newborn session at home', 'A newborn photo, portrait. Sessions page and the home page sessions list.'),
 'session-family': ('images/sessions/family.jpg', 1333, 2000, 'Family session', 'A family photo, portrait. Sessions page and the home page sessions list.'),
 'session-milestones': ('images/sessions/milestones.jpg', 1333, 2000, 'Graduation portrait', 'A graduation or 18th photo, portrait. Sessions page and the home page sessions list.'),
 'about-portrait': ('images/about/portrait.jpg', 1333, 2000, 'The photographer behind Sunday Light, with her camera', 'A photo of Charne, ideally with her camera. About page.'),
}
WEDDING_KEYS = [k for k, v in PHOTOS.items() if v[0].startswith(W)]
assert len(WEDDING_KEYS) == 23

# Extra portfolio galleries. Each one appears once its photos exist.
EXTRA_GALLERIES = [
 ('couples', 'Couples', 'images/portfolio/couples-{:02d}.jpg', 6, 'Couples session'),
 ('family', 'Family', 'images/portfolio/family-{:02d}.jpg', 8, 'Family session'),
 ('bump-newborn', 'Bump & newborn', 'images/portfolio/bump-newborn-{:02d}.jpg', 6, 'Bump or newborn session'),
]

# Portfolio order: getting ready, the party, portraits, golden hour
PORTFOLIO_WEDDINGS = ['arch-mirror', 'gilded-mirror', 'bridesmaids-seated', 'bridesmaids-steps', 'groomsmen-steps',
                      'castle-laugh', 'castle-window', 'castle-dip', 'castle-balcony', 'bougainvillea-bride',
                      'bougainvillea-embrace', 'silver-car-bouquet', 'car-window-smile', 'winery-champagne',
                      'olive-grove-confetti', 'dam-kiss', 'jaguar-window-kiss', 'jaguar-veil', 'jaguar-flare',
                      'jaguar-kiss', 'field-dusk', 'grass-overhead', 'vineyard-sunset']
assert sorted(PORTFOLIO_WEDDINGS) == sorted(WEDDING_KEYS)

SESSIONS = [
 dict(id='weddings', name='Weddings', photo='bougainvillea-embrace',
      card='The whole day or just the vows. Calm, unposed and full of light.',
      body=['I photograph weddings the way they feel: getting ready, the nerves, the vows, the champagne and the dance floor.',
            'I keep things calm and quiet, step in when you need direction and stay out of the way when you don’t. '
            'I’ll also help you plan the timeline, so your portraits land in the best light of the day.']),
 dict(id='couples', name='Couples', photo='field-dusk',
      card='Engagements, proposals, anniversaries, or just because.',
      body=['Engagements, anniversaries or no reason at all. We’ll walk, talk and wander somewhere beautiful as the sun goes down.',
            'Planning a proposal? I can stay out of sight nearby and catch the moment you ask.']),
 dict(id='bump', name='Bump', photo='session-bump',
      card='Maternity sessions on the beach, in the hills or at home.',
      body=['Somewhere between 28 and 36 weeks is usually the sweet spot, while you’re still comfortable and the bump is beautifully round.',
            'On the beach, in a paddock or at home. Partners and big brothers and sisters are very welcome.']),
 dict(id='newborn', name='Newborn', photo='session-newborn',
      card='Relaxed lifestyle sessions at home in the first few weeks.',
      body=['Relaxed lifestyle sessions at home in the first few weeks, while they’re still tiny and sleepy.',
            'No complicated props. Just your baby, your family and the soft light from your own windows.']),
 dict(id='family', name='Family', photo='session-family',
      card='Beach walks and paddock afternoons. Kids and dogs welcome.',
      body=['Beach walks, golden paddocks and gum trees, or a slow afternoon at home.',
            'Kids get to be kids. I’ll do the work of catching the moments in between.']),
 dict(id='milestones', name='Milestones', photo='session-milestones',
      card='Graduations, 18ths and the days worth remembering.',
      body=['Graduations, 18ths, birthdays and the days worth marking.',
            'Short, easy sessions that make the most of a big day.']),
]

STRIP = [('castle-dip', 'p'), ('olive-grove-confetti', 'l'), ('jaguar-flare', 'p'),
         ('car-window-smile', 'p'), ('bridesmaids-seated', 'l'), ('dam-kiss', 'p')]

STEPS = [
 ('Say hello', 'Tell me who you are, what you’re after and roughly when. I’ll come back with dates and details.'),
 ('Plan it together', 'We’ll choose a spot and a time. For outdoor sessions that usually means the last hour before sunset.'),
 ('The session', 'Relaxed and unrushed. I’ll give you easy prompts, so you’re never left wondering what to do with your hands.'),
 ('Your gallery', 'Your edited photos arrive in a private online gallery, ready to download and share.'),
]

WEAR = [
 ('Soft, natural colours', 'Cream, white, linen, sage, rust and denim all photograph beautifully in warm light.'),
 ('Coordinate, don’t match', 'Pick two or three colours and mix them across the family.'),
 ('Texture over pattern', 'Knits, linen and flowing dresses move well. Busy prints pull focus from faces.'),
 ('Skip logos and neon', 'They’re the first thing your eye goes to in a photo.'),
 ('Shoes you can walk in', 'And a layer for when the sun drops.'),
]

FAQ = [
 ('When is the best time for a session?',
  'For outdoor sessions, the hour before sunset. In summer that’s often from about 7.30pm, and in winter from about 4pm. I’ll suggest a start time when we book.'),
 ('Where do sessions happen?',
  'Anywhere that means something to you: the beach, the hills, a favourite park or your own home. If you’re not sure, I’m happy to suggest a few spots.'),
 ('What if the weather turns?',
  'We’ll keep an eye on the forecast together and move to a new date if we need to.'),
 ('How do we get our photos?',
  'In a private online gallery, ready to download and share with family.'),
 ('Can you help us with what to wear?',
  'Yes. Once you’ve booked I’ll send through some ideas, and you’re welcome to send me photos of your options.'),
]

INSTAGRAM = ('@cwatson.creative', 'https://www.instagram.com/cwatson.creative/')
ENDPOINT = 'https://lumenadl.app.n8n.cloud/webhook/sunday-light-enquiry'

# Where to centre photos that get cropped hard, such as the wide band at the foot of each page.
FOCUS = {
    'winery-champagne': '50% 62%',
    'olive-grove-confetti': '50% 55%',
    'jaguar-flare': '50% 36%',
    'castle-window': '50% 36%',
}
