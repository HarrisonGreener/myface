#!/usr/bin/env python3
"""Builds the My Face static site.

Edit CONFIG and the content below, then run:  python3 build.py
Every page, the sitemap and the structured data are regenerated from here.
"""
import html, json, os, shutil

# ---------------------------------------------------------------- settings
CONFIG = {
    "site_url": "https://www.example.com",   # your real domain, no trailing slash
    "brand": "My Face",
    "tagline": "your face, your space",  # not shown in the minimal layout
    "owner": "[YOUR NAME]",
    "town": "Droylsden",                     # where the home studio is
    "city": "Manchester",                    # the bigger search area
    "region": "Greater Manchester",
    "served": ["Droylsden", "Manchester", "Oldham", "Ashton-under-Lyne", "Failsworth", "Denton", "Audenshaw"],
    "phone": "[PHONE NUMBER]",
    "email": "[EMAIL]",
    "instagram": "https://www.instagram.com/[HANDLE]",
    "booking_url": "[BOOKING LINK]",       # e.g. your Fresha / Booksy / Square link
}
C = CONFIG
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- content
# Prices are estimates based on typical home-salon prices around Tameside and Oldham.
CATEGORIES = [
    {
        "slug": "hair", "name": "Hair",
        "blurb": "Cuts, colour, styling and extensions",
        "intro": "<p>Whether it's a tidy-up, a full change of colour or extra length, hair appointments start with a proper chat about what you want and what will suit your hair.</p>",
        "services": [
            {"slug": "cuts-and-styling", "name": "Haircuts & Styling",
             "short": "Cuts, restyles and blow-dries for all hair types.",
             "intro": "<p>From a trim to keep your ends healthy to a complete restyle, every cut starts with a consultation so we agree on the shape, length and how you style it day to day.</p><p>Blow-dries and occasion hair are available on their own, too, for nights out, weddings and photos.</p>",
             "expect": ["A consultation about the look you want and your routine", "Wash and condition", "Cut and finish, with tips for styling it at home"],
             "time": "45–90 minutes",
             "prices": [("Cut & blow-dry", "£28"), ("Restyle", "£35"), ("Blow-dry", "£18"), ("Hair up / occasion", "from £30"), ("Fringe trim", "£5")],
             "faqs": [("How often should I get a trim?", "Most people book every 6–12 weeks depending on length and style. Shorter, sharper cuts need trimming more often to keep their shape."),
                      ("Can I bring a picture?", "Yes, please do. Pictures are the easiest way to show the look you're after.")]},
            {"slug": "colour", "name": "Hair Colour",
             "short": "Roots, full colour, highlights, balayage and toners.",
             "intro": "<p>Colour includes root touch-ups, all-over colour, highlights, balayage and toners. Bigger changes, like going much lighter, may take more than one appointment to keep your hair in good condition.</p>",
             "expect": ["A colour consultation and strand check", "A skin patch test at least 48 hours before your appointment", "Colour, tone, wash and finish"],
             "time": "1.5–4 hours",
             "prices": [("Root tint", "£40"), ("Full head colour", "from £50"), ("Half-head highlights", "from £55"), ("Full-head highlights", "from £70"), ("Balayage", "from £85"), ("Toner", "£20")],
             "faqs": [("Do I need a patch test?", "Yes. A skin patch test is needed at least 48 hours before any colour service, even if you've had colour before, because allergies can develop over time."),
                      ("Can you take me from dark to blonde in one go?", "Sometimes, but often it's safer done over a few sessions. You'll get an honest answer at your consultation about what's realistic for your hair.")]},
            {"slug": "extensions", "name": "Hair Extensions",
             "short": "Tape-in and clip-in extensions for length and volume.",
             "intro": "<p>Extensions add length, thickness or a pop of colour. The shade and texture are matched to your own hair, and you'll be shown how to look after them.</p>",
             "expect": ["Consultation and colour match", "Fitting and blending", "Cut and styling to finish"],
             "time": "1.5–3 hours",
             "prices": [("Tape-in extensions (full head)", "from £150"), ("Tape-in refit", "from £70"), ("Clip-in fitting & blend", "£30"), ("Removal", "£25")],
             "faqs": [("How long do tape-ins last?", "Tape-ins are usually moved up every 6–8 weeks, and good quality hair can be reused for several refits."),
                      ("Will they damage my hair?", "Fitted and removed properly, and looked after at home, extensions shouldn't cause damage. Never remove them yourself.")]},
        ],
    },
    {
        "slug": "nails", "name": "Nails",
        "blurb": "Gel, BIAB, acrylics and nail art",
        "intro": "<p>Clean natural sets, long sculpted acrylics, chrome, charms and full hand-painted art.</p>",
        "services": [
            {"slug": "gel-nails", "name": "Gel Nails",
             "short": "Gel polish on natural nails that lasts for weeks.",
             "intro": "<p>Gel polish is cured under a lamp, so it's dry the moment you leave and stays glossy without chipping. It's a good choice if you want colour on your natural nails without extensions.</p>",
             "expect": ["Nail prep, shaping and cuticle care", "Gel colour, cured under a lamp", "Top coat and cuticle oil"],
             "time": "45 minutes",
             "prices": [("Gel polish, hands", "£20"), ("Gel polish, toes", "£20"), ("Hands & toes", "£35"), ("Removal (no new set)", "£5")],
             "faqs": [("How long does gel polish last?", "Usually around 2–3 weeks, depending on how fast your nails grow and what you do with your hands."),
                      ("Should I peel it off?", "No. Peeling gel takes layers of your natural nail with it. Book a removal instead.")]},
            {"slug": "biab", "name": "BIAB Nails",
             "short": "Builder gel that strengthens your own nails.",
             "intro": "<p>BIAB (builder in a bottle) is a thicker builder gel applied over your natural nails. It adds strength, so it's popular with anyone trying to grow their nails out, and it can be infilled rather than fully removed each time.</p>",
             "expect": ["Prep and shaping", "Builder gel to strengthen and shape the nail", "Colour or natural finish"],
             "time": "1 hour",
             "prices": [("BIAB overlay", "£28"), ("BIAB infill", "£25"), ("BIAB with French or chrome", "£33")],
             "faqs": [("How often do I need an infill?", "Most people come back every 3–4 weeks."),
                      ("Can I have art on top?", "Yes, BIAB works well under colour, French tips, chrome and art.")]},
            {"slug": "acrylic-nails", "name": "Acrylic Nails",
             "short": "Sculpted extensions in any length and shape.",
             "intro": "<p>Acrylic extensions are built from liquid and powder to give you length and a strong shape: square, coffin, almond, stiletto, whatever you're into.</p>",
             "expect": ["Prep of the natural nail", "Tips or sculpting to your chosen length and shape", "Colour, art or charms to finish"],
             "time": "1.5–2 hours",
             "prices": [("Full set", "£32"), ("Full set, extra long", "£38"), ("Infill", "£25"), ("Removal", "£10")],
             "faqs": [("How often do acrylics need infills?", "Usually every 2–3 weeks to keep them strong and balanced as your nails grow."),
                      ("What length can I go?", "Pretty much any. We'll talk through what's practical for your day-to-day.")]},
            {"slug": "nail-art", "name": "Nail Art",
             "short": "Hand-painted designs, chrome, gems and charms.",
             "intro": "<p>Bring a picture, a mood or just a colour, and the design gets built around it. Hand-painted art, chrome, 3D gel, gems and charms are all on the menu.</p>",
             "expect": ["A chat about the design", "Base set of your choice", "Art priced by detail"],
             "time": "Depends on the design",
             "prices": [("Accent nails (2)", "from £5"), ("Full set art", "from £10"), ("Chrome", "£5"), ("Charms & gems", "from £1 each")],
             "faqs": [("Can I book nail art on its own?", "It's added to a gel, BIAB or acrylic set. Send the design when you book so enough time is set aside."),
                      ("How is art priced?", "By detail and how many nails, from simple accents to a full set.")]},
        ],
    },
    {
        "slug": "beauty", "name": "Beauty",
        "blurb": "Lashes, brows, waxing and make-up",
        "intro": "<p>The finishing touches: lashes, brows, waxing and make-up for everyday or big occasions.</p>",
        "services": [
            {"slug": "lashes", "name": "Lash Lifts & Extensions",
             "short": "Lifted, tinted natural lashes or full extensions.",
             "intro": "<p>A lash lift curls your own lashes from the root and is usually paired with a tint, so they look longer and darker without mascara. Extensions add length and fullness lash by lash.</p>",
             "expect": ["A patch test before your first lift, tint or extensions", "Lift and tint, or extensions applied", "Aftercare advice to make them last"],
             "time": "1–2 hours",
             "prices": [("Lash lift & tint", "£35"), ("Classic extensions, full set", "£45"), ("Hybrid, full set", "£50"), ("Russian volume, full set", "£55"), ("Infills", "from £25")],
             "faqs": [("How long does a lash lift last?", "Usually around 6–8 weeks, as your lashes naturally shed and regrow."),
                      ("Do I need a patch test?", "Yes, at least 24–48 hours before your first appointment.")]},
            {"slug": "brows", "name": "Brows",
             "short": "Shaping, tinting and brow lamination.",
             "intro": "<p>Brow appointments include shaping, tinting and lamination, which sets your brow hairs in a brushed-up, fuller-looking shape.</p>",
             "expect": ["Brow mapping to suit your face", "Shape, tint or lamination", "A finishing brow gel"],
             "time": "20–45 minutes",
             "prices": [("Brow wax", "£8"), ("Brow wax & tint", "£15"), ("Brow lamination & tint", "£32"), ("Lamination, tint & lash lift", "£60")],
             "faqs": [("How long does brow lamination last?", "Usually around 6–8 weeks."),
                      ("Can I have a tint and lamination together?", "Yes, they're usually booked together.")]},
            {"slug": "waxing", "name": "Waxing",
             "short": "Smooth results for face and body.",
             "intro": "<p>Quick, clean waxing for face and body. Hair needs to be a little grown out for wax to grip, roughly the length of a grain of rice.</p>",
             "expect": ["Skin prep", "Wax suited to the area", "Soothing aftercare"],
             "time": "10–45 minutes",
             "prices": [("Lip or chin", "£6"), ("Underarm", "£10"), ("Bikini", "from £12"), ("Half leg", "£18"), ("Full leg", "£28")],
             "faqs": [("How long should my hair be?", "Around 0.5 cm, or about 2–3 weeks of growth after shaving."),
                      ("Can I wax if I use retinoids?", "Say so when you book. Some skincare products make skin more sensitive to waxing.")]},
            {"slug": "makeup", "name": "Make-up",
             "short": "Make-up for nights out, prom, events and shoots.",
             "intro": "<p>Make-up for birthdays, nights out, prom, weddings and shoots, from soft and natural to full glam.</p>",
             "expect": ["A chat about the look and your outfit", "Skin prep", "Full make-up, lashes optional"],
             "time": "45–75 minutes",
             "prices": [("Natural make-up", "£30"), ("Full glam", "£40"), ("Prom make-up", "£40"), ("Strip lashes added", "£5")],
             "faqs": [("Do you do bridal make-up?", "[YES/NO — add details]"),
                      ("Should I come with a clean face?", "Yes, ideally moisturised with no make-up on.")]},
        ],
    },
    {
        "slug": "piercing", "name": "Piercing",
        "blurb": "Ear, nose and navel piercing",
        "intro": "<p>Piercings are done by [PIERCER / QUALIFICATIONS] using [METHOD], in a clean space registered with the council, with jewellery to choose from. Prices include basic jewellery.</p><p>Age policy: [YOUR AGE POLICY]. Photo ID may be asked for.</p>",
        "services": [
            {"slug": "ear-piercing", "name": "Ear Piercing",
             "short": "Lobes, helix, tragus, conch and more.",
             "intro": "<p>From first lobes to a full curated ear: lobe, upper lobe, helix, forward helix, tragus, conch, daith and more. You'll get help planning placements that suit your ear shape.</p>",
             "expect": ["Choose your placement and jewellery", "Marking and a check in the mirror", "Piercing, then aftercare advice"],
             "time": "20–30 minutes",
             "prices": [("Single lobe", "£20"), ("Pair of lobes", "£30"), ("Helix or forward helix", "£25"), ("Tragus", "£25"), ("Conch or daith", "£30")],
             "faqs": [("How long do ear piercings take to heal?", "Lobes usually take around 6–8 weeks. Cartilage piercings like the helix or conch can take 6–12 months or more."),
                      ("When can I change the jewellery?", "Only once it's healed. Come back and it can be checked and changed for you.")]},
            {"slug": "nose-piercing", "name": "Nose Piercing",
             "short": "Nostril and septum piercings.",
             "intro": "<p>Nostril and septum piercings, placed to suit your face, with jewellery to choose from.</p>",
             "expect": ["Choose placement and jewellery", "Marking and checking", "Piercing and aftercare advice"],
             "time": "20–30 minutes",
             "prices": [("Nostril", "£25"), ("Septum", "£30")],
             "faqs": [("How long does a nose piercing take to heal?", "A nostril usually takes around 4–6 months, and a septum around 2–3 months, sometimes longer."),
                      ("Does it hurt?", "There's a quick, sharp pinch. Most people say it's over faster than they expected.")]},
            {"slug": "navel-piercing", "name": "Navel Piercing",
             "short": "Belly button piercings.",
             "intro": "<p>Navel (belly button) piercings, with a quick anatomy check first to make sure the piercing will sit and heal well.</p>",
             "expect": ["Anatomy check", "Choose jewellery", "Piercing and aftercare advice"],
             "time": "30 minutes",
             "prices": [("Navel", "£30")],
             "faqs": [("How long does a navel piercing take to heal?", "Usually around 6–12 months."),
                      ("Can everyone get a navel piercing?", "Not always. It depends on your anatomy, which gets checked before piercing.")]},
        ],
    },
    {
        "slug": "filler", "name": "Filler",
        "blurb": "Lip and dermal filler",
        "intro": "<p>Filler treatments are carried out by [PRACTITIONER / QUALIFICATIONS], using hyaluronic acid fillers. Every treatment starts with a consultation and a medical history check.</p><p><strong>Over-18s only.</strong> It's illegal in England to give cosmetic filler to anyone under 18, and ID will be checked.</p>",
        "services": [
            {"slug": "lip-filler", "name": "Lip Filler",
             "short": "Volume, shape and hydration for lips.",
             "intro": "<p>Lip filler adds volume, defines shape or balances the lips using a hyaluronic acid gel. Results can be kept subtle, and you can build up over more than one appointment.</p><p>Hyaluronic acid filler is temporary and gradually breaks down. Lip filler commonly lasts around 6 months, though it varies from person to person.</p>",
             "expect": ["Consultation, medical history and consent", "Numbing, then filler placed in small amounts", "Aftercare advice and a review appointment"],
             "time": "45 minutes",
             "prices": [("0.5ml lip filler", "£75"), ("1ml lip filler", "£100"), ("Consultation", "Free")],
             "faqs": [("How long does lip filler last?", "Often around 6 months, but it varies depending on the product, the amount and your body."),
                      ("Will I swell?", "Some swelling and bruising is normal for a few days. It settles, and your final result shows after about two weeks."),
                      ("Who can't have filler?", "Anyone under 18, and anyone pregnant or breastfeeding. Some medical conditions and medications also rule it out, which gets checked at consultation.")]},
            {"slug": "dermal-filler", "name": "Dermal Filler",
             "short": "Chin, cheek and jawline filler.",
             "intro": "<p>Dermal filler can add volume and contour to areas such as the chin, cheeks and jawline. Everything is planned at a consultation so results look like you.</p><p>Hyaluronic acid filler is temporary. How long it lasts depends on the area and product, which is explained at consultation.</p>",
             "expect": ["Consultation, medical history and consent", "Treatment", "Aftercare advice and a review appointment"],
             "time": "45–60 minutes",
             "prices": [("Chin (1ml)", "from £100"), ("Cheeks (1ml)", "from £110"), ("Jawline (2ml)", "from £180"), ("Consultation", "Free")],
             "faqs": [("Is filler permanent?", "No. Hyaluronic acid fillers break down naturally over time."),
                      ("Are there risks?", "As with any injectable treatment, there are risks. Most side effects are mild, like swelling and bruising, and serious complications are rare. They'll be talked through with you before treatment.")]},
        ],
    },
]

AREAS = [
    {"slug": "droylsden", "name": "Droylsden",
     "body": f"<p>{C['brand']} is a home beauty studio in Droylsden, Tameside. It's appointment-only, and the full address is sent once you've booked.</p><p>It's handy for anyone in Droylsden, Fairfield, Littlemoss, Audenshaw and Clayton.</p>"},
    {"slug": "manchester", "name": "Manchester",
     "body": f"<p>Looking for nails, lashes, hair, piercing or lip filler in east Manchester? {C['brand']} is in Droylsden, about four miles east of the city centre, with the Metrolink Droylsden stop on the East Manchester line.</p><p>Clients come over from Clayton, Openshaw, Gorton and across the city. It's appointment-only, and you'll get the address when you book.</p>"},
    {"slug": "oldham", "name": "Oldham",
     "body": f"<p>{C['brand']} is a short drive from Oldham, Failsworth and Chadderton, at a home studio in Droylsden. It's appointment-only, and you'll get the address when you book.</p>"},
]

AFTERCARE = [
    {"slug": "piercing", "name": "Piercing Aftercare",
     "body": "<ul><li>Clean twice a day with sterile saline spray. No alcohol, tea tree or harsh soaps.</li><li>Don't twist or turn the jewellery, and try not to touch it except when cleaning, with clean hands.</li><li>Avoid sleeping on new ear piercings. A travel pillow helps.</li><li>Keep it out of pools, hot tubs, the sea and baths until it's healed.</li><li>Some redness, swelling and clear or whitish fluid is normal early on.</li><li>Don't take the jewellery out to change it until it's fully healed.</li><li>If you see spreading redness, heat, yellow or green discharge, or feel unwell, get in touch and see a GP or pharmacist.</li></ul>"},
    {"slug": "filler", "name": "Filler Aftercare",
     "body": "<ul><li>Avoid touching or massaging the area for 24 hours unless you've been told to.</li><li>Skip make-up on the area for 12–24 hours.</li><li>Avoid alcohol, strenuous exercise, saunas and heat for 24–48 hours.</li><li>Swelling and bruising are normal and usually settle within a few days. A cold compress can help.</li><li>Your final result shows after around two weeks. Come back for your review appointment.</li><li><strong>Get help straight away</strong> if you notice severe or worsening pain, skin that turns white, blue or blotchy, or any changes to your vision. Contact us immediately, and call 999 or go to A&amp;E if you can't reach us.</li></ul>"},
    {"slug": "lashes-and-brows", "name": "Lash & Brow Aftercare",
     "body": "<ul><li>Keep lashes and brows dry for 24 hours after a lift, tint or lamination. No steam, saunas or swimming.</li><li>Avoid mascara and brow products for 24 hours.</li><li>For extensions, use oil-free products and brush them gently every day.</li><li>Don't pick or pull at extensions. Book a removal instead.</li></ul>"},
    {"slug": "nails", "name": "Nail Aftercare",
     "body": "<ul><li>Use cuticle oil daily to keep nails and skin healthy.</li><li>Wear gloves for cleaning and washing up.</li><li>Don't use your nails as tools for opening cans or scraping labels.</li><li>Never pick or peel off gel, BIAB or acrylics. Book a removal.</li><li>If a nail lifts or breaks, get in touch so it can be fixed before water gets underneath.</li></ul>"},
]

GENERAL_FAQS = [
    ("Where are you?", f"{C['brand']} is a home studio in {C['town']}, Tameside. The full address is sent once you've booked."),
    ("What are your opening hours?", "There aren't set opening hours. It's appointment-only, so pick a time that suits you on the booking page."),
    ("How do I book?", f"Book online through the <a href=\"{C['booking_url']}\">booking page</a>, message on Instagram or call {C['phone']}."),
    ("Do you do mobile appointments?", "[YES/NO — add details]"),
    ("Do you take deposits?", "[YOUR DEPOSIT POLICY]"),
    ("What's your cancellation policy?", "[YOUR CANCELLATION POLICY]"),
    ("Do I need a patch test?", "Yes, for hair colour, lash and brow tints, lash lifts and lash extensions. Patch tests need to be done 24–48 hours before your appointment."),
    ("Is there an age limit?", "Filler is over-18s only by law in England. For piercings the policy is [YOUR AGE POLICY]. For other treatments, under-16s need a parent or guardian with them."),
    ("How do I pay?", "[PAYMENT METHODS]"),
]

# ---------------------------------------------------------------- desktop apps (homepage computer)
ICONS = {
    "nails": '<path d="M9 3h6v4H9zM8 7h8l1 13a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1z"/><path d="M10 12h4"/>',
    "hair": '<circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path d="M8 16 19 3M16 16 5 3"/>',
    "beauty": '<path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path d="M5 7 3 4M12 5V2M19 7l2-3"/>',
    "piercing": '<circle cx="12" cy="14" r="6"/><path d="M12 2v6"/><circle cx="12" cy="2.5" r="1.2"/>',
    "filler": '<path d="M2 12c3-4 6-5 10-2 4-3 7-2 10 2-3 5-6 7-10 7S5 17 2 12z"/><path d="M2 12h20"/>',
    "prices": '<path d="M15 5a4 4 0 0 0-7 3v11M6 12h7M5 19h12"/>',
    "book": '<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="m9 15 2 2 4-4"/>',
    "about": '<circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "contact": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/>',
    "web": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "her": '<path d="m12 3 2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
}

# ---------------------------------------------------------------- helpers
e = html.escape
PAGES = []  # (path, priority)


def rel(depth, target):
    return ("../" * depth) + target if (depth or target) else "./"


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def logo(d):
    return f'<a class="logo" href="{rel(d, "")}" aria-label="{e(C["brand"])} home">my<b>face</b></a>'


def page(path, title, desc, h1, main, crumbs=(), schema=None, priority="0.6", home=False):
    d = path.count("/")
    nav = [("Hair", "hair/"), ("Nails", "nails/"), ("Beauty", "beauty/"), ("Piercing", "piercing/"),
           ("Filler", "filler/"), ("Prices", "prices/"), ("FAQ", "faq/")]
    cur = ' aria-current="page"'
    navh = "".join(f'<a href="{rel(d, t)}"{cur if path.startswith(t) else ""}>{n}</a>' for n, t in nav)
    url = C["site_url"] + "/" + path
    crumb_list = [("Home", "")] + list(crumbs)
    graphs = [business_schema()]
    if crumbs:
        graphs.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": C["site_url"] + "/" + p} for i, (n, p) in enumerate(crumb_list)]})
    graphs += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graphs}, ensure_ascii=False).replace("</", "<\\/")
    if home:
        body = main
    else:
        bc = '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(
            f'<a href="{rel(d, p)}">{e(n)}</a>' if p != path else f"<span>{e(n)}</span>" for n, p in crumb_list) + "</nav>"
        body = f"""<main id="content" class="wrap">
{bc}
<article class="win page-win">
<div class="titlebar"><span>myface://{e(path.rstrip("/") or "home")}</span><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span></div>
<div class="win-body">
<h1>{e(h1)}</h1>
{main}
</div>
</article>
</main>"""
    area_links = " · ".join(f'<a href="{rel(d, "areas/" + a["slug"] + "/")}">{e(a["name"])}</a>' for a in AREAS)
    doc = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(C['brand'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta name="theme-color" content="#efe9e4">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(d, 'assets/style.css')}">
<script>document.documentElement.className='js'</script>
<script type="application/ld+json">{ld}</script>
</head>
<body{' class="home"' if home else ''}>
<a class="skip" href="#content">Skip to content</a>
<header class="top"><div class="wrap bar">{logo(d)}<nav class="nav" aria-label="Main">{navh}</nav><a class="btn" href="{e(C['booking_url'])}">Book</a></div></header>
{body}
<footer class="foot"><div class="wrap">
<p>{e(C['brand'])} · home beauty studio in {e(C['town'])} · near {area_links}</p>
<p><a href="{rel(d, 'services/')}">All treatments</a> · <a href="{rel(d, 'aftercare/')}">Aftercare</a> · <a href="{rel(d, 'about/')}">About</a> · <a href="{rel(d, 'gallery/')}">Gallery</a> · <a href="{rel(d, 'contact/')}">Contact</a> · <a href="{rel(d, 'privacy/')}">Privacy</a> · <a href="{rel(d, 'terms/')}">Terms</a></p>
<p>&copy;2026 {e(C['brand'])}</p>
</div></footer>
<script src="{rel(d, 'assets/site.js')}" defer></script>
</body>
</html>
"""
    target = os.path.join(OUT, "404.html") if path == "404.html" else os.path.join(OUT, path, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(doc)
    if path != "404.html":
        PAGES.append((path, priority))


def business_schema():
    return {"@type": "BeautySalon", "@id": C["site_url"] + "/#business", "name": C["brand"], "url": C["site_url"] + "/",
            "telephone": C["phone"], "email": C["email"], "sameAs": [C["instagram"]], "priceRange": "££",
            "address": {"@type": "PostalAddress", "addressLocality": C["town"], "addressRegion": C["region"], "addressCountry": "GB"},
            "areaServed": [{"@type": "Place", "name": a} for a in C["served"]]}


def sec(title, body):
    return f'<section class="sec"><h2>{title}</h2>{body}</section>'


def faq_html(faqs):
    return "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faqs)


def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in faqs]}


def links(d, items):
    """A minimal menu list: name on the left, price or note on the right."""
    return '<ul class="menu">' + "".join(
        f'<li><a href="{rel(d, href)}">{e(name)}</a><span>{e(sub)}</span></li>' for name, sub, href in items) + "</ul>"


def price_table(rows):
    return '<table class="prices">' + "".join(f'<tr><th scope="row">{e(n)}</th><td>{e(p)}</td></tr>' for n, p in rows) + "</table>"


def from_price(s):
    for _, p in s["prices"]:
        if "£" in p:
            return "from £" + p.split("£")[1]
    return ""


def cta(d):
    return f'<p class="cta"><a class="btn" href="{e(C["booking_url"])}">Book a slot</a> <a class="btn ghost" href="{rel(d, "contact/")}">Ask a question</a></p>'


def myspace():
    """The MySpace-style profile that lives on the computer screen."""
    nav = [("Home", ""), ("Hair", "hair/"), ("Nails", "nails/"), ("Beauty", "beauty/"), ("Piercing", "piercing/"), ("Filler", "filler/"),
           ("Prices", "prices/"), ("Aftercare", "aftercare/"), ("FAQ", "faq/"), ("Contact", "contact/")]
    navh = " | ".join(f'<a href="{h or "./"}">{n}</a>' for n, h in nav)
    services = "".join(
        f'<tr><th scope="row">{e(c["name"])}</th><td>' + ", ".join(f'<a href="{c["slug"]}/{s["slug"]}/">{e(s["name"])}</a>' for s in c["services"]) + "</td></tr>"
        for c in CATEGORIES)
    picks = ["gel-nails", "biab", "acrylic-nails", "lashes", "ear-piercing", "colour", "lip-filler"]
    allsv = {s["slug"]: (s, c) for c in CATEGORIES for s in c["services"]}
    top = '<li><a href="about/"><span class="thumb her"><span class="mascot mini"></span></span>her.exe<small>Top friend</small></a></li>' + "".join(
        f'<li><a href="{allsv[k][1]["slug"]}/{k}/"><span class="thumb">[pic]</span>{e(allsv[k][0]["name"])}<small>{from_price(allsv[k][0])}</small></a></li>' for k in picks)
    comments = "".join(
        f'<tr><td class="c-who"><span class="thumb sm">[pic]</span><a href="#">[Client name]</a></td><td><b class="date">[date]</b><p>[Paste a real client review here]</p></td></tr>' for _ in range(3))
    return f"""<div class="ms">
<div class="ms-top"><span class="ms-logo">my<b>face</b><i>.com</i></span><span class="ms-tag">your face, your space</span>
<form class="ms-search" role="search" action="services/"><label for="q">Search treatments</label><input id="q" name="q" placeholder="Search treatments"><button>Search</button></form></div>
<nav class="ms-nav" aria-label="Profile">{navh}</nav>
<div class="ms-page">
<div class="ms-left">
<h2 class="ms-name">{e(C['brand'])}</h2>
<div class="ms-profile">
<span class="pic"><span class="mascot"></span></span>
<div class="ms-info"><p>"Hair, nails, lashes, piercings &amp; lips, all in one place."</p>
<p>Home beauty studio<br>{e(C['town'])}<br>{e(C['city'])}<br>United Kingdom</p>
<p class="online"><span></span> Online Now!</p>
<p>Last Login: today</p></div></div>
<p class="viewmy">View My: <a href="prices/">Prices</a> | <a href="gallery/">Pics</a> | <a href="aftercare/">Aftercare</a></p>
<div class="ms-box contact"><h3>Contacting {e(C['brand'])}</h3>
<div class="actions"><a href="{e(C['booking_url'])}">&#10148; Book Appointment</a><a href="contact/">&#10148; Send Message</a><a href="{e(C['instagram'])}">&#10148; Add to Friends</a><a href="tel:{e(C['phone'])}">&#10148; Call Me</a></div></div>
<div class="ms-box url"><b>{e(C['brand'])} URL:</b><br>myface.co.uk/book</div>
<div class="ms-box"><h3>{e(C['brand'])}'s Services</h3><table>{services}</table></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Details</h3><table>
<tr><th scope="row">Status:</th><td>Taking bookings</td></tr>
<tr><th scope="row">Here for:</th><td>Fresh sets, new hair, a lil sparkle</td></tr>
<tr><th scope="row">Hometown:</th><td>{e(C['town'])}, Tameside</td></tr>
<tr><th scope="row">Hours:</th><td>Appointment only, address sent when you book</td></tr></table></div>
</div>
<div class="ms-right">
<div class="ms-net"><b>{e(C['brand'])} is in your extended network</b></div>
<div class="ms-player"><button type="button" id="radio" aria-label="Play">&#9654;</button><span><b>My Face Radio</b><br><span id="np">press play for salon vibes</span></span></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Latest Blog Entries</h3><ul class="blog">
<li>[OFFER] new client discount on your first set (<a href="nails/">view more</a>)</li>
<li>[NEWS] new piercing jewellery just landed (<a href="piercing/">view more</a>)</li>
<li>Full price list (<a href="prices/">view more</a>)</li></ul></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Blurbs</h3>
<h4>About me:</h4><p>[A few lines about you.] {e(C['brand'])} is a home beauty studio in {e(C['town'])} for nails, hair, lashes, brows, piercing and lip filler.</p>
<h4>Who I'd like to meet:</h4><p>Anyone after a fresh set, a new colour, a little sparkle in their ear or a bit of lip.</p></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Friend Space</h3><p class="fs-count">{e(C['brand'])} has <b>8</b> treatments in their Top 8.</p><ul class="top8">{top}</ul>
<p class="all"><a href="services/">View all treatments</a></p></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Friends Comments</h3><table class="comments">{comments}</table></div>
</div>
</div>
<p class="ms-foot"><a href="about/">About</a> | <a href="faq/">FAQ</a> | <a href="terms/">Terms</a> | <a href="privacy/">Privacy</a> | <a href="areas/">Areas</a><br>&copy;2026 {e(C['brand'])}. All Rights Reserved.</p>
</div>"""


def desktop():
    """The computer's desktop: app icons, pop-up windows and a taskbar."""
    apps = [("web", "myface.com", "web", "./", myspace())]
    for c in CATEGORIES:
        body = f'<p>{e(c["blurb"])}.</p>' + links(0, [(s["name"], from_price(s), f'{c["slug"]}/{s["slug"]}/') for s in c["services"]]) + \
               f'<p class="win-foot"><a href="{c["slug"]}/">Open {e(c["name"].lower())} page &rarr;</a></p>'
        apps.append((c["slug"], c["name"], c["slug"], f'{c["slug"]}/', body))
    price_rows = "".join(f'<tr><th scope="row"><a href="{c["slug"]}/{s["slug"]}/">{e(s["name"])}</a></th><td>{from_price(s)}</td></tr>'
                         for c in CATEGORIES for s in c["services"])
    apps.append(("prices", "Prices", "prices", "prices/", f'<table class="prices">{price_rows}</table><p class="win-foot"><a href="prices/">Full price list &rarr;</a></p>'))
    apps.append(("book", "Book", "book", C["booking_url"],
                 f'<p>Appointment-only home studio in {e(C["town"])}. Pick a time online and the address is sent once you\'ve booked.</p>'
                 f'<p><a class="btn" href="{e(C["booking_url"])}">Book a slot</a></p><p class="win-foot"><a href="faq/">Booking FAQs &rarr;</a></p>'))
    apps.append(("her", "her.exe", "her", "about/",
                 '<div class="spin"><button type="button" class="avatar-btn" id="avatarBtn" aria-label="Spin the My Face mascot">'
                 '<span class="mascot" id="mascot" role="img" aria-label="The My Face mascot: an emo girl with black and pink hair"></span></button>'
                 '<p class="bubble" id="bubble" aria-live="polite">drag me round x</p></div>'))
    apps.append(("about", "About", "about", "about/",
                 f'<p>{e(C["brand"])} is a home beauty studio in {e(C["town"])}, Tameside, for hair, nails, lashes, brows, piercing and lip filler.</p>'
                 f'<p>[A line or two about you.]</p><p class="win-foot"><a href="about/">More about me &rarr;</a></p>'))
    apps.append(("contact", "Contact", "contact", "contact/",
                 f'<ul class="plain"><li><a href="tel:{e(C["phone"])}">{e(C["phone"])}</a></li><li><a href="mailto:{e(C["email"])}">{e(C["email"])}</a></li>'
                 f'<li><a href="{e(C["instagram"])}">Instagram</a></li></ul><p class="win-foot"><a href="contact/">Contact page &rarr;</a></p>'))
    icons = "".join(f'<li><a class="app" href="{e(href)}" data-app="{k}">{icon(ic)}<span>{e(label)}</span></a></li>' for k, label, ic, href, _ in apps)
    wins = "".join(f'<section class="win app-win{" web" if k == "web" else ""}" id="win-{k}" hidden aria-label="{e(label)}">'
                   f'<div class="titlebar"><span>{e(label)}</span><button type="button" class="close" aria-label="Close {e(label)}">&times;</button></div>'
                   f'<div class="win-body">{body}</div></section>' for k, label, ic, href, body in apps)
    return f"""<div class="os" id="os">
<ul class="apps">{icons}</ul>
{wins}
<div class="taskbar"><span class="start">myface</span><span id="clock">--:--</span></div>
<div class="boot" id="boot" aria-hidden="true"><pre id="bootlog"></pre></div>
</div>"""


def computer():
    keys = "".join('<i></i>' for _ in range(56))
    box = '<div class="f fr"></div><div class="f bk"></div><div class="f lf"></div><div class="f rt"></div><div class="f tp"></div><div class="f bt"></div>'
    return f"""<main id="content" class="room">
<div class="scene" id="scene">
<div class="rig" id="rig">
<div class="monitor box">
<div class="f fr front"><div class="screen" id="screen">{desktop()}<span class="glare"></span></div>
<button type="button" class="zoom-btn" id="zoomBtn" aria-label="Zoom into the computer screen"></button></div>
<div class="f bk"></div><div class="f lf"></div><div class="f rt"></div><div class="f tp"></div><div class="f bt"></div>
</div>
<div class="tube box">{box}</div>
<div class="neck box">{box}</div>
<div class="foot box">{box}</div>
<div class="kbd box"><div class="f fr"></div><div class="f bk"></div><div class="f lf"></div><div class="f rt"></div><div class="f tp keys">{keys}</div><div class="f bt"></div></div>
<div class="shadow"></div>
</div>
</div>
<p class="hint" id="hint">click the computer to turn it on</p>
</div>
<div class="zoomview" id="zoomview" hidden><div class="zv-screen" id="zvScreen"></div>
<button type="button" class="logoff" id="logoff">log off</button></div>
<div class="caption">
<h1>Hair, nails, lashes, piercing &amp; lip filler in {e(C['town'])}</h1>
<p>An appointment-only home beauty studio in {e(C['town'])}, near Manchester and Oldham.</p>
<p><a class="btn" href="{e(C['booking_url'])}">Book a slot</a> <a class="btn ghost" href="services/">All treatments</a></p>
</div>
</main>"""


# ---------------------------------------------------------------- build
def build():
    for f in os.listdir(OUT):
        p = os.path.join(OUT, f)
        if os.path.isdir(p) and f not in ("assets", ".git") and os.path.exists(os.path.join(p, "index.html")):
            shutil.rmtree(p)
    town, city = C["town"], C["city"]

    page("", f"{C['brand']} | Nails, Hair, Lashes, Piercing & Lip Filler in {town}, {city}",
         f"{C['brand']} is an appointment-only home beauty studio in {town}, near Manchester and Oldham: gel and acrylic nails, BIAB, lashes, brows, hair, ear and nose piercing, and lip filler.",
         "", computer(), priority="1.0", home=True)

    page("services/", f"Treatments in {town}, {city} | {C['brand']}",
         f"All nail, hair, lash, brow, piercing and filler treatments at {C['brand']}, a home beauty studio in {town}.",
         "All treatments",
         "".join(sec(f'<a href="../{c["slug"]}/">{e(c["name"])}</a>', links(1, [(s["name"], from_price(s), f'{c["slug"]}/{s["slug"]}/') for s in c["services"]])) for c in CATEGORIES) + cta(1),
         crumbs=[("Treatments", "services/")], priority="0.9")

    for c in CATEGORIES:
        cp = f'{c["slug"]}/'
        page(cp, f"{c['name']} in {town}, {city} | {C['brand']}",
             f"{c['blurb']} at {C['brand']}, a home studio in {town} near Manchester and Oldham. " + " ".join(s["short"] for s in c["services"])[:90],
             f"{c['name']} in {town}",
             c["intro"] + sec("Menu", links(1, [(s["name"], from_price(s), f'{cp}{s["slug"]}/') for s in c["services"]]))
             + sec("Prices", "".join(f'<h3><a href="{s["slug"]}/">{e(s["name"])}</a></h3>' + price_table(s["prices"]) for s in c["services"]))
             + cta(1),
             crumbs=[(c["name"], cp)], priority="0.9")
        for s in c["services"]:
            sp = f'{cp}{s["slug"]}/'
            others = [(o["name"], from_price(o), f'{cp}{o["slug"]}/') for o in c["services"] if o is not s]
            care = {"piercing": "piercing", "filler": "filler", "nails": "nails"}.get(c["slug"])
            if s["slug"] in ("lashes", "brows"):
                care = "lashes-and-brows"
            care_name = {"piercing": "piercing", "filler": "filler", "nails": "nail", "lashes-and-brows": "lash &amp; brow"}.get(care)
            care_html = f'<p><a href="../../aftercare/{care}/">Read the {care_name} aftercare guide &rarr;</a></p>' if care else ""
            offers = [{"@type": "Offer", "name": n, "priceCurrency": "GBP", "price": p.split("£")[1].split(" ")[0]} for n, p in s["prices"] if "£" in p]
            page(sp, f"{s['name']} in {town}, {city} | {C['brand']}",
                 f"{s['name']} in {town}, {from_price(s)}. {s['short']} Appointment-only home studio near Manchester and Oldham.",
                 f"{s['name']} in {town}",
                 s["intro"]
                 + sec("Prices", price_table(s["prices"]) + "<p class=\"note\">Prices are a guide and are confirmed at booking.</p>")
                 + sec("What to expect", "<ol>" + "".join(f"<li>{x}</li>" for x in s["expect"]) + f"</ol><p><strong>Time:</strong> {e(s['time'])}</p>{care_html}")
                 + sec("FAQs", faq_html(s["faqs"]))
                 + (sec(f"More {c['name'].lower()}", links(2, others)) if others else "")
                 + cta(2),
                 crumbs=[(c["name"], cp), (s["name"], sp)], priority="0.8",
                 schema=[{"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["short"],
                          "provider": {"@id": C["site_url"] + "/#business"}, "areaServed": C["served"], "offers": offers}, faq_schema(s["faqs"])])

    rows = "".join(sec(f'<a href="../{c["slug"]}/">{e(c["name"])}</a>',
                       "".join(f'<h3><a href="../{c["slug"]}/{s["slug"]}/">{e(s["name"])}</a></h3>' + price_table(s["prices"]) for s in c["services"]))
                   for c in CATEGORIES)
    page("prices/", f"Price List | Nails, Hair, Lashes & Filler in {town} | {C['brand']}",
         f"Prices for nails, hair, lashes, brows, waxing, piercing and lip filler at {C['brand']} in {town}, Manchester.",
         "Price list", rows + "<p class=\"note\">Prices are a guide and are confirmed at booking.</p>" + cta(1),
         crumbs=[("Prices", "prices/")], priority="0.8")

    page("areas/", f"Areas Covered | {C['brand']}", f"{C['brand']} is a home beauty studio in {town}, close to Manchester, Oldham and the rest of Tameside.",
         "Areas we cover", links(1, [(a["name"], "", f'areas/{a["slug"]}/') for a in AREAS]),
         crumbs=[("Areas", "areas/")], priority="0.6")
    for a in AREAS:
        ap = f'areas/{a["slug"]}/'
        menu = "".join(sec(f'<a href="../../{c["slug"]}/">{e(c["name"])} near {e(a["name"])}</a>',
                           links(2, [(s["name"], from_price(s), f'{c["slug"]}/{s["slug"]}/') for s in c["services"]])) for c in CATEGORIES)
        page(ap, f"Nails, Lashes, Hair, Piercing & Lip Filler near {a['name']} | {C['brand']}",
             f"Looking for nails, lashes, hair, piercing or lip filler near {a['name']}? {C['brand']} is an appointment-only home beauty studio in {town}.",
             f"Beauty near {a['name']}", a["body"] + menu + cta(2),
             crumbs=[("Areas", "areas/"), (a["name"], ap)], priority="0.7")

    page("aftercare/", f"Aftercare Guides | {C['brand']}", f"Aftercare advice for piercings, filler, lashes, brows and nails from {C['brand']} in {town}.",
         "Aftercare guides", links(1, [(a["name"], "", f'aftercare/{a["slug"]}/') for a in AFTERCARE]),
         crumbs=[("Aftercare", "aftercare/")], priority="0.6")
    for a in AFTERCARE:
        ap = f'aftercare/{a["slug"]}/'
        page(ap, f"{a['name']} | {C['brand']}", f"{a['name']}: how to look after your treatment from {C['brand']} in {town}.",
             a["name"], a["body"] + "<p class=\"note\">This is general advice. If you're worried about anything, get in touch or speak to a GP or pharmacist.</p>" + cta(2),
             crumbs=[("Aftercare", "aftercare/"), (a["name"], ap)], priority="0.5")

    page("faq/", f"FAQs | {C['brand']}, {town}", f"Answers about booking, the home studio, deposits, patch tests and age limits at {C['brand']} in {town}.",
         "Frequently asked questions", faq_html(GENERAL_FAQS) + cta(1),
         crumbs=[("FAQ", "faq/")], schema=[faq_schema(GENERAL_FAQS)], priority="0.6")
    page("about/", f"About {C['owner']} | {C['brand']}, {town}", f"Meet {C['owner']}, the face behind {C['brand']}, a home beauty studio in {town}.",
         f"About {C['owner']}", "<p>[Your story: how you got into hair and beauty, your training and qualifications, and what makes an appointment with you different.]</p>"
         + sec("Qualifications &amp; insurance", "<ul><li>[QUALIFICATION]</li><li>[QUALIFICATION]</li><li>[INSURANCE / COUNCIL REGISTRATION]</li></ul>") + cta(1),
         crumbs=[("About", "about/")], priority="0.5")
    page("gallery/", f"Gallery | {C['brand']}, {town}", f"Photos of nails, hair, lashes, piercings and more by {C['brand']} in {town}.",
         "Gallery", '<div class="grid">' + "".join(f'<a class="ph" href="../{c["slug"]}/{s["slug"]}/">[{e(s["name"])} photo]</a>' for c in CATEGORIES for s in c["services"]) + "</div>",
         crumbs=[("Gallery", "gallery/")], priority="0.5")
    page("contact/", f"Contact & Booking | {C['brand']}, {town}", f"Book or get in touch with {C['brand']}, an appointment-only home beauty studio in {town}.",
         "Contact & booking",
         f'<ul class="plain"><li>Book: <a href="{e(C["booking_url"])}">online booking</a></li><li>Call: <a href="tel:{e(C["phone"])}">{e(C["phone"])}</a></li><li>Email: <a href="mailto:{e(C["email"])}">{e(C["email"])}</a></li><li>Instagram: <a href="{e(C["instagram"])}">message us</a></li></ul>'
         + sec("Where to find us", f"<p>{C['brand']} is a home studio in {town}, Tameside. It's appointment-only with no walk-ins, and the full address is sent once you've booked.</p><p>Close to <a href=\"../areas/manchester/\">Manchester</a>, <a href=\"../areas/oldham/\">Oldham</a> and the rest of Tameside.</p>"),
         crumbs=[("Contact", "contact/")], priority="0.7")
    page("privacy/", f"Privacy Policy | {C['brand']}", f"How {C['brand']} uses and protects your information.", "Privacy policy",
         "<p>[Your privacy policy: what you collect (booking details, consultation and medical forms), why, how long you keep it, and how clients can ask for it or have it deleted under UK GDPR.]</p>",
         crumbs=[("Privacy", "privacy/")], priority="0.2")
    page("terms/", f"Terms & Booking Policy | {C['brand']}", f"Booking, deposit and cancellation terms at {C['brand']}.", "Terms & booking policy",
         "<p>[Deposits, cancellations, late arrivals, refunds and redos.]</p>", crumbs=[("Terms", "terms/")], priority="0.2")
    page("404.html", f"Page not found | {C['brand']}", "This page couldn't be found.", "Error 404",
         f'<p>That page doesn\'t exist. Try the <a href="{C["site_url"]}/">homepage</a> or the <a href="{C["site_url"]}/services/">treatments list</a>.</p>')

    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p, pr in PAGES:
            f.write(f"  <url><loc>{C['site_url']}/{p}</loc><priority>{pr}</priority></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {C['site_url']}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages + 404, sitemap.xml and robots.txt")


if __name__ == "__main__":
    build()
