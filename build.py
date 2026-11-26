#!/usr/bin/env python3
"""Builds the MyFace static site.

Edit CONFIG and the content below, then run:  python3 build.py
Every page, the sitemap and the structured data are regenerated from here.
"""
import html, json, os, shutil

# ---------------------------------------------------------------- settings
CONFIG = {
    "site_url": "https://harrisongreener.github.io/myface",   # change to the real domain when there is one, no trailing slash
    "brand": "MyFace",
    "tagline": "customise your avatar",
    "owner": "Ella Moore",
    "town": "Manchester",                    # main area the business is known by
    "city": "Manchester",                    # the bigger search area
    "region": "Greater Manchester",
    "served": ["Manchester", "Droylsden", "Oldham", "Stockport", "Ashton-under-Lyne", "Failsworth", "Denton", "Audenshaw"],
    "phone": "[PHONE NUMBER]",
    "email": "[EMAIL]",
    "instagram": "https://www.instagram.com/[HANDLE]",
    "booking_url": "[BOOKING LINK]",       # e.g. your Fresha / Booksy / Square link
}
C = CONFIG
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- content
# Prices are estimates based on typical home-salon prices around Greater Manchester.
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
     "body": f"<p>{C['brand']} is a home beauty studio in Manchester that also covers Droylsden, Fairfield, Audenshaw and Clayton. It's appointment-only, and you'll get the address once you've booked.</p>"},
    {"slug": "oldham", "name": "Oldham",
     "body": f"<p>{C['brand']} is a home beauty studio in Manchester that also covers Oldham, Failsworth and Chadderton. It's appointment-only, and you'll get the address once you've booked.</p>"},
    {"slug": "stockport", "name": "Stockport",
     "body": f"<p>{C['brand']} is a home beauty studio in Manchester that also covers Stockport, Denton and Reddish. It's appointment-only, and you'll get the address once you've booked.</p>"},
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
    ("Where are you?", f"{C['brand']} is a home studio in {C['town']}, covering Droylsden, Oldham, Stockport and the surrounding areas. The full address is sent once you've booked."),
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
SEARCH = []  # (title, description, path) for the site search


def rel(depth, target):
    return ("../" * depth) + target if (depth or target) else "./"


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def logo(d):
    return f'<a class="logo" href="{rel(d, "")}">{logo_svg("logo-svg")}<span class="sr">{e(C["brand"])} home</span></a>'


def page(path, title, desc, h1, main, crumbs=(), schema=None, priority="0.6", home=False):
    d = path.count("/")
    nav = [("Home", ""), ("Hair", "hair/"), ("Nails", "nails/"), ("Beauty", "beauty/"), ("Piercing", "piercing/"),
           ("Filler", "filler/"), ("Prices", "prices/"), ("FAQ", "faq/")]
    cur = ' aria-current="page"'
    navh = "".join(f'<a href="{rel(d, t)}"{cur if (path.startswith(t) if t else path == "") else ""}>{n}</a>' for n, t in nav)
    # bubble menu: the same links, with a sub-ring of treatments for each category
    def bl(label, href, sub=None):
        inner = "" if not sub else "<ul>" + "".join(f'<li><a href="{rel(d, h)}">{e(n)}</a></li>' for n, h in sub) + "</ul>"
        url = rel(d, href) if (href == "" or href.endswith("/")) and not href.startswith("http") else href
        return f'<li><a href="{e(url)}"{cur if href and path == href else ""}>{e(label)}</a>{inner}</li>'
    bubbles = bl("Home", "") + bl("Book a slot", C["booking_url"])
    for c in CATEGORIES:
        bubbles += bl(c["name"], c["slug"] + "/", [(sv["name"], f'{c["slug"]}/{sv["slug"]}/') for sv in c["services"]] + [("All " + c["name"].lower(), c["slug"] + "/")])
    bubbles += (bl("Prices", "prices/") + bl("Aftercare", "aftercare/") + bl("FAQ", "faq/") + bl("Gallery", "gallery/")
                + bl("About Ella", "about/") + bl("Contact", "contact/"))
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
<div class="titlebar"><a class="back" href="{rel(d, crumb_list[-2][1] if len(crumb_list) > 1 else "")}" data-back>&larr; Back</a><span class="tpath">myface://{e(path.rstrip("/") or "home")}</span><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span></div>
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
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Bagel+Fat+One&family=Pixelify+Sans:wght@400;600&family=Inter:wght@400;600&family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(d, 'assets/style.css')}?v=56">
<script>document.documentElement.className='js'</script>
<script type="application/ld+json">{ld}</script>
</head>
<body{' class="home"' if home else ''}>
{LOGO_DEFS}
<a class="skip" href="#content">Skip to content</a>
<header class="top"><div class="wrap bar"><div class="brand">{logo(d)}<svg class="tag-svg" viewBox="28 0 460 44" role="img" aria-label="{e(C['tagline'])}"><text class="tt" x="70" y="32" textLength="382" lengthAdjust="spacing" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-weight="500" letter-spacing="1" font-size="34" fill="#1c1a1e">{e(C['tagline'])}</text></svg></div><nav class="nav" aria-label="Main">{navh}</nav><button type="button" class="orb-btn" id="menuBtn" aria-expanded="false" aria-controls="bubbleNav"><span class="pk"></span>Menu</button><a class="btn" href="{e(C['booking_url'])}"><span class="pk"></span>Book</a><button type="button" class="orb-btn search-btn" id="searchBtn" aria-label="Search the site" data-index="{rel(d, 'assets/search.json')}?v=56" data-root="{rel(d, '')}"><svg class="mg" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6.5"/><path d="M15 15l6 6"/></svg><span class="sl">Search</span></button></div></header>
<nav class="bubble-nav" id="bubbleNav" aria-label="Menu" hidden><ul>{bubbles}</ul></nav>
{body}
<footer class="foot"><div class="wrap">
<p>{e(C['brand'])} · home beauty studio in {e(C['town'])} · near {area_links}</p>
<p><a href="{rel(d, 'services/')}">All treatments</a> · <a href="{rel(d, 'aftercare/')}">Aftercare</a> · <a href="{rel(d, 'about/')}">About</a> · <a href="{rel(d, 'gallery/')}">Gallery</a> · <a href="{rel(d, 'contact/')}">Contact</a> · <a href="{rel(d, 'privacy/')}">Privacy</a> · <a href="{rel(d, 'terms/')}">Terms</a></p>
<p>&copy;2026 {e(C['brand'])}</p>
<p class="credit">Designed &amp; built by <a href="https://harrisongreener.co.uk" target="_blank" rel="noopener">Harrison Greener</a></p>
</div></footer>
<script src="{rel(d, 'assets/site.js')}?v=56" defer></script>
</body>
</html>
"""
    target = os.path.join(OUT, "404.html") if path == "404.html" else os.path.join(OUT, path, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(doc)
    if path != "404.html":
        PAGES.append((path, priority))
        SEARCH.append({"t": h1 or "Home", "d": desc, "u": path})


def business_schema():
    return {"@type": "BeautySalon", "@id": C["site_url"] + "/#business", "name": C["brand"], "url": C["site_url"] + "/",
            "telephone": C["phone"], "email": C["email"], "sameAs": [C["instagram"]], "priceRange": "££",
            "address": {"@type": "PostalAddress", "addressLocality": C["town"], "addressRegion": C["region"], "addressCountry": "GB"},
            "areaServed": [{"@type": "Place", "name": a} for a in C["served"]],
            "founder": {"@type": "Person", "name": C["owner"]}}


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
<div class="ms-top"><span class="ms-logo"><svg class="ms-logo-svg" viewBox="26 24 530 200" role="img" aria-label="{e(C['brand'])}"><use href="#mf-chrome"/></svg><i>.com</i></span><span class="ms-tag">{e(C['tagline'])}</span>
<form class="ms-search" role="search" action="services/"><label for="q">Search treatments</label><input id="q" name="q" placeholder="Search treatments"><button>Search</button></form></div>
<nav class="ms-nav" aria-label="Profile">{navh}</nav>
<div class="ms-page">
<div class="ms-left">
<h2 class="ms-name">{e(C['owner'])} &hearts;</h2>
<div class="ms-profile">
<span class="pic"><img class="pic-img" src="assets/ella-px.png" alt="Photo of {e(C['owner'])}" width="106" height="140"></span>
<div class="ms-info"><p>"Hair, nails, lashes, piercings &amp; lips, all in one place."</p>
<p>Home beauty studio<br>{e(C['town'])}<br>United Kingdom</p>
<p class="online"><span></span> Online Now!</p>
<p>Last Login: today</p></div></div>
<p class="viewmy">View My: <a href="prices/">Prices</a> | <a href="gallery/">Pics</a> | <a href="aftercare/">Aftercare</a></p>
<div class="ms-box contact"><h3>Contacting {e(C['owner'].split()[0])}</h3>
<div class="actions"><a href="{e(C['booking_url'])}">&#10148; Book Appointment</a><a href="contact/">&#10148; Send Message</a><a href="{e(C['instagram'])}">&#10148; Add to Friends</a><a href="tel:{e(C['phone'])}">&#10148; Call Me</a></div></div>
<div class="ms-box url"><b>{e(C['brand'])} URL:</b><br>myface.co.uk/book</div>
<div class="ms-box"><h3>{e(C['brand'])}'s Services</h3><table>{services}</table></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Details</h3><table>
<tr><th scope="row">Status:</th><td>Taking bookings</td></tr>
<tr><th scope="row">Here for:</th><td>Fresh sets, new hair, a lil sparkle</td></tr>
<tr><th scope="row">Hometown:</th><td>{e(C['town'])}</td></tr>
<tr><th scope="row">Hours:</th><td>Appointment only, address sent when you book</td></tr></table></div>
</div>
<div class="ms-right">
<div class="ms-net"><b>{e(C['brand'])} is in your extended network</b></div>
<div class="ms-player"><button type="button" id="radio" aria-label="Play">&#9654;</button><button type="button" id="radioNext" aria-label="Next track">&#9654;&#9654;</button><span class="np-wrap"><b>MyFace Radio</b> &middot; The Money Store<br><span id="np" aria-live="polite">press play x</span></span><a class="am-badge" id="amLink" href="https://music.apple.com/gb/album/the-money-store/515449028" target="_blank" rel="noopener">Listen on Apple&nbsp;Music</a></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Latest Blog Entries</h3><ul class="blog">
<li>[OFFER] new client discount on your first set (<a href="nails/">view more</a>)</li>
<li>[NEWS] new piercing jewellery just landed (<a href="piercing/">view more</a>)</li>
<li>Full price list (<a href="prices/">view more</a>)</li></ul></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Blurbs</h3>
<h4>About me:</h4><p>Hi, I'm {e(C['owner'].split()[0])}! [A few lines about you.] {e(C['brand'])} is my home beauty studio in {e(C['town'])} for nails, hair, lashes, brows, piercing and lip filler.</p>
<h4>Who I'd like to meet:</h4><p>Anyone after a fresh set, a new colour, a little sparkle in their ear or a bit of lip.</p></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Friend Space</h3><p class="fs-count">{e(C['brand'])} has <b>8</b> treatments in their Top 8.</p><ul class="top8">{top}</ul>
<p class="all"><a href="services/">View all treatments</a></p></div>
<div class="ms-box"><h3>{e(C['brand'])}'s Friends Comments</h3><table class="comments">{comments}</table></div>
</div>
</div>
<p class="ms-foot">Designed &amp; built by <a href="https://harrisongreener.co.uk" target="_blank" rel="noopener">Harrison Greener</a><br><a href="about/">About</a> | <a href="faq/">FAQ</a> | <a href="terms/">Terms</a> | <a href="privacy/">Privacy</a> | <a href="areas/">Areas</a><br>&copy;2026 {e(C['brand'])}. All Rights Reserved.</p>
</div>"""


LOGO_VB = "28 4 460 168"
LOGO_DEFS = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><filter id="mf-wob" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.02 0.05" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter><filter id="mf-wob-big" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.02 0.05" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="12"/></filter><pattern id="mf-stripes" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="14" height="14" fill="#e6e6ea"/><rect width="6" height="14" fill="#d6d3dc"/></pattern><pattern id="mf-dots" width="13" height="11" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1.2" fill="#7d7a84"/><circle cx="9" cy="8" r=".9" fill="#d23c86"/><rect x="6" y="1" width="2" height="1" fill="#333"/></pattern><symbol id="mf-letters" viewBox="0 0 520 170"><text x="72" y="124" font-family="Bagel Fat One, Arial Black, sans-serif" font-size="108" fill="#2a2630" transform="rotate(-10 116 100)">m</text><text x="156" y="138" font-family="Courier New, Courier, monospace" font-weight="700" font-size="112" fill="#3b3742" transform="rotate(14 190 100)">y</text><text x="212" y="116" font-family="Pirata One, serif" font-size="134" fill="#d23c86" transform="rotate(-8 240 90) skewX(-12)">F</text><text x="262" y="134" font-family="Georgia, Times New Roman, serif" font-style="italic" font-size="104" fill="#b8306f" transform="rotate(9 292 105)">a</text><text x="318" y="122" font-family="Impact, Haettenschweiler, Arial Black, sans-serif" font-size="110" fill="#e0559b" transform="rotate(-14 348 95) skewX(8)">c</text><text x="370" y="140" font-family="Bagel Fat One, Arial Black, sans-serif" font-size="96" fill="#d23c86" transform="rotate(12 402 110)">E</text></symbol><symbol id="mf-logo" viewBox="28 4 460 168"><g filter="url(#mf-wob)"><use href="#mf-letters" width="520" height="170"/></g></symbol><linearGradient id="mf-cp" x1="0" y1="0" x2="0.15" y2="1"><stop offset="0" stop-color="#fff3fa"/><stop offset="0.34" stop-color="#ffb0d8"/><stop offset="0.5" stop-color="#b8306f"/><stop offset="0.56" stop-color="#ffe6f3"/><stop offset="0.8" stop-color="#ff7fbf"/><stop offset="1" stop-color="#8f2253"/></linearGradient><linearGradient id="mf-ck" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="#8b8796"/><stop offset="0.42" stop-color="#2a2630"/><stop offset="0.5" stop-color="#050406"/><stop offset="0.56" stop-color="#6d6878"/><stop offset="1" stop-color="#141117"/></linearGradient><linearGradient id="mf-cs" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="0.42" stop-color="#b9b9cc"/><stop offset="0.5" stop-color="#5f5f75"/><stop offset="0.56" stop-color="#f7f7ff"/><stop offset="1" stop-color="#7d7d93"/></linearGradient><linearGradient id="mf-cw" gradientUnits="userSpaceOnUse" x1="0" y1="114" x2="0" y2="142"><stop offset="0" stop-color="#fff"/><stop offset="0.5" stop-color="#7c7c92"/><stop offset="1" stop-color="#e8e8f4"/></linearGradient><clipPath id="mf-front"><rect x="150" y="0" width="70" height="240"/><rect x="388" y="0" width="70" height="240"/></clipPath><symbol id="mf-chrome" viewBox="26 24 530 200"><g transform="rotate(-5 290 128)"><g fill="none" stroke-linecap="round"><path d="M36 136.4 L42 136.9 L48 137.0 L54 136.8 L60 136.2 L66 135.3 L72 134.1 L78 132.6 L84 131.0 L90 129.3 L96 127.5 L102 125.7 L108 124.0 L114 122.5 L120 121.2 L126 120.2 L132 119.4 L138 119.1 L144 119.0 L150 119.4 L156 120.0 L162 121.0 L168 122.3 L174 123.8 L180 125.5 L186 127.3 L192 129.0 L198 130.8 L204 132.4 L210 133.9 L216 135.1 L222 136.1 L228 136.7 L234 137.0 L240 136.9 L246 136.5 L252 135.7 L258 134.6 L264 133.3 L270 131.7 L276 130.0 L282 128.2 L288 126.4 L294 124.7 L300 123.1 L306 121.7 L312 120.5 L318 119.7 L324 119.2 L330 119.0 L336 119.2 L342 119.7 L348 120.6 L354 121.8 L360 123.2 L366 124.8 L372 126.5 L378 128.3 L384 130.1 L390 131.8 L396 133.3 L402 134.7 L408 135.7 L414 136.5 L420 136.9 L426 137.0 L432 136.7 L438 136.1 L444 135.1 L450 133.9 L456 132.4 L462 130.7 L468 129.0 L474 127.2 L480 125.4 L486 123.7 L492 122.3 L498 121.0 L504 120.0 L510 119.3 L516 119.0 L522 119.1 L528 119.5 L534 120.2 L540 121.2 L546 122.6" stroke="#0e0a0d" stroke-width="7"/><path d="M36 119.6 L42 119.1 L48 119.0 L54 119.2 L60 119.8 L66 120.7 L72 121.9 L78 123.4 L84 125.0 L90 126.7 L96 128.5 L102 130.3 L108 132.0 L114 133.5 L120 134.8 L126 135.8 L132 136.6 L138 136.9 L144 137.0 L150 136.6 L156 136.0 L162 135.0 L168 133.7 L174 132.2 L180 130.5 L186 128.7 L192 127.0 L198 125.2 L204 123.6 L210 122.1 L216 120.9 L222 119.9 L228 119.3 L234 119.0 L240 119.1 L246 119.5 L252 120.3 L258 121.4 L264 122.7 L270 124.3 L276 126.0 L282 127.8 L288 129.6 L294 131.3 L300 132.9 L306 134.3 L312 135.5 L318 136.3 L324 136.8 L330 137.0 L336 136.8 L342 136.3 L348 135.4 L354 134.2 L360 132.8 L366 131.2 L372 129.5 L378 127.7 L384 125.9 L390 124.2 L396 122.7 L402 121.3 L408 120.3 L414 119.5 L420 119.1 L426 119.0 L432 119.3 L438 119.9 L444 120.9 L450 122.1 L456 123.6 L462 125.3 L468 127.0 L474 128.8 L480 130.6 L486 132.3 L492 133.7 L498 135.0 L504 136.0 L510 136.7 L516 137.0 L522 136.9 L528 136.5 L534 135.8 L540 134.8 L546 133.4" stroke="#0e0a0d" stroke-width="7"/><path d="M85.2 118L103.2 138M85.2 138L103.2 118M179.5 118L197.5 138M179.5 138L197.5 118M273.7 118L291.7 138M273.7 138L291.7 118M368.0 118L386.0 138M368.0 138L386.0 118M462.2 118L480.2 138M462.2 138L480.2 118" stroke="#0e0a0d" stroke-width="6"/><path d="M36 136.4 L42 136.9 L48 137.0 L54 136.8 L60 136.2 L66 135.3 L72 134.1 L78 132.6 L84 131.0 L90 129.3 L96 127.5 L102 125.7 L108 124.0 L114 122.5 L120 121.2 L126 120.2 L132 119.4 L138 119.1 L144 119.0 L150 119.4 L156 120.0 L162 121.0 L168 122.3 L174 123.8 L180 125.5 L186 127.3 L192 129.0 L198 130.8 L204 132.4 L210 133.9 L216 135.1 L222 136.1 L228 136.7 L234 137.0 L240 136.9 L246 136.5 L252 135.7 L258 134.6 L264 133.3 L270 131.7 L276 130.0 L282 128.2 L288 126.4 L294 124.7 L300 123.1 L306 121.7 L312 120.5 L318 119.7 L324 119.2 L330 119.0 L336 119.2 L342 119.7 L348 120.6 L354 121.8 L360 123.2 L366 124.8 L372 126.5 L378 128.3 L384 130.1 L390 131.8 L396 133.3 L402 134.7 L408 135.7 L414 136.5 L420 136.9 L426 137.0 L432 136.7 L438 136.1 L444 135.1 L450 133.9 L456 132.4 L462 130.7 L468 129.0 L474 127.2 L480 125.4 L486 123.7 L492 122.3 L498 121.0 L504 120.0 L510 119.3 L516 119.0 L522 119.1 L528 119.5 L534 120.2 L540 121.2 L546 122.6" stroke="url(#mf-cw)" stroke-width="3.5"/><path d="M36 119.6 L42 119.1 L48 119.0 L54 119.2 L60 119.8 L66 120.7 L72 121.9 L78 123.4 L84 125.0 L90 126.7 L96 128.5 L102 130.3 L108 132.0 L114 133.5 L120 134.8 L126 135.8 L132 136.6 L138 136.9 L144 137.0 L150 136.6 L156 136.0 L162 135.0 L168 133.7 L174 132.2 L180 130.5 L186 128.7 L192 127.0 L198 125.2 L204 123.6 L210 122.1 L216 120.9 L222 119.9 L228 119.3 L234 119.0 L240 119.1 L246 119.5 L252 120.3 L258 121.4 L264 122.7 L270 124.3 L276 126.0 L282 127.8 L288 129.6 L294 131.3 L300 132.9 L306 134.3 L312 135.5 L318 136.3 L324 136.8 L330 137.0 L336 136.8 L342 136.3 L348 135.4 L354 134.2 L360 132.8 L366 131.2 L372 129.5 L378 127.7 L384 125.9 L390 124.2 L396 122.7 L402 121.3 L408 120.3 L414 119.5 L420 119.1 L426 119.0 L432 119.3 L438 119.9 L444 120.9 L450 122.1 L456 123.6 L462 125.3 L468 127.0 L474 128.8 L480 130.6 L486 132.3 L492 133.7 L498 135.0 L504 136.0 L510 136.7 L516 137.0 L522 136.9 L528 136.5 L534 135.8 L540 134.8 L546 133.4" stroke="url(#mf-cw)" stroke-width="3.5"/><path d="M85.2 118L103.2 138M85.2 138L103.2 118M179.5 118L197.5 138M179.5 138L197.5 118M273.7 118L291.7 138M273.7 138L291.7 118M368.0 118L386.0 138M368.0 138L386.0 118M462.2 118L480.2 138M462.2 138L480.2 118" stroke="url(#mf-cw)" stroke-width="3"/></g></g><g font-family="Bagel Fat One, Arial Black, sans-serif" font-size="128" text-anchor="middle"><text x="290" y="160" fill="#000" stroke="#000" stroke-width="30" stroke-linejoin="round" transform="translate(6 8)">myface</text><text x="290" y="160" fill="#fff" stroke="#fff" stroke-width="22" stroke-linejoin="round">myface</text><text x="290" y="160" stroke="#3a1a2c" stroke-width="2.5"><tspan fill="url(#mf-ck)">my</tspan><tspan fill="url(#mf-cp)">face</tspan></text></g><g transform="rotate(-5 290 128)" clip-path="url(#mf-front)"><g fill="none" stroke-linecap="round"><path d="M36 136.4 L42 136.9 L48 137.0 L54 136.8 L60 136.2 L66 135.3 L72 134.1 L78 132.6 L84 131.0 L90 129.3 L96 127.5 L102 125.7 L108 124.0 L114 122.5 L120 121.2 L126 120.2 L132 119.4 L138 119.1 L144 119.0 L150 119.4 L156 120.0 L162 121.0 L168 122.3 L174 123.8 L180 125.5 L186 127.3 L192 129.0 L198 130.8 L204 132.4 L210 133.9 L216 135.1 L222 136.1 L228 136.7 L234 137.0 L240 136.9 L246 136.5 L252 135.7 L258 134.6 L264 133.3 L270 131.7 L276 130.0 L282 128.2 L288 126.4 L294 124.7 L300 123.1 L306 121.7 L312 120.5 L318 119.7 L324 119.2 L330 119.0 L336 119.2 L342 119.7 L348 120.6 L354 121.8 L360 123.2 L366 124.8 L372 126.5 L378 128.3 L384 130.1 L390 131.8 L396 133.3 L402 134.7 L408 135.7 L414 136.5 L420 136.9 L426 137.0 L432 136.7 L438 136.1 L444 135.1 L450 133.9 L456 132.4 L462 130.7 L468 129.0 L474 127.2 L480 125.4 L486 123.7 L492 122.3 L498 121.0 L504 120.0 L510 119.3 L516 119.0 L522 119.1 L528 119.5 L534 120.2 L540 121.2 L546 122.6" stroke="#0e0a0d" stroke-width="7"/><path d="M36 119.6 L42 119.1 L48 119.0 L54 119.2 L60 119.8 L66 120.7 L72 121.9 L78 123.4 L84 125.0 L90 126.7 L96 128.5 L102 130.3 L108 132.0 L114 133.5 L120 134.8 L126 135.8 L132 136.6 L138 136.9 L144 137.0 L150 136.6 L156 136.0 L162 135.0 L168 133.7 L174 132.2 L180 130.5 L186 128.7 L192 127.0 L198 125.2 L204 123.6 L210 122.1 L216 120.9 L222 119.9 L228 119.3 L234 119.0 L240 119.1 L246 119.5 L252 120.3 L258 121.4 L264 122.7 L270 124.3 L276 126.0 L282 127.8 L288 129.6 L294 131.3 L300 132.9 L306 134.3 L312 135.5 L318 136.3 L324 136.8 L330 137.0 L336 136.8 L342 136.3 L348 135.4 L354 134.2 L360 132.8 L366 131.2 L372 129.5 L378 127.7 L384 125.9 L390 124.2 L396 122.7 L402 121.3 L408 120.3 L414 119.5 L420 119.1 L426 119.0 L432 119.3 L438 119.9 L444 120.9 L450 122.1 L456 123.6 L462 125.3 L468 127.0 L474 128.8 L480 130.6 L486 132.3 L492 133.7 L498 135.0 L504 136.0 L510 136.7 L516 137.0 L522 136.9 L528 136.5 L534 135.8 L540 134.8 L546 133.4" stroke="#0e0a0d" stroke-width="7"/><path d="M85.2 118L103.2 138M85.2 138L103.2 118M179.5 118L197.5 138M179.5 138L197.5 118M273.7 118L291.7 138M273.7 138L291.7 118M368.0 118L386.0 138M368.0 138L386.0 118M462.2 118L480.2 138M462.2 138L480.2 118" stroke="#0e0a0d" stroke-width="6"/><path d="M36 136.4 L42 136.9 L48 137.0 L54 136.8 L60 136.2 L66 135.3 L72 134.1 L78 132.6 L84 131.0 L90 129.3 L96 127.5 L102 125.7 L108 124.0 L114 122.5 L120 121.2 L126 120.2 L132 119.4 L138 119.1 L144 119.0 L150 119.4 L156 120.0 L162 121.0 L168 122.3 L174 123.8 L180 125.5 L186 127.3 L192 129.0 L198 130.8 L204 132.4 L210 133.9 L216 135.1 L222 136.1 L228 136.7 L234 137.0 L240 136.9 L246 136.5 L252 135.7 L258 134.6 L264 133.3 L270 131.7 L276 130.0 L282 128.2 L288 126.4 L294 124.7 L300 123.1 L306 121.7 L312 120.5 L318 119.7 L324 119.2 L330 119.0 L336 119.2 L342 119.7 L348 120.6 L354 121.8 L360 123.2 L366 124.8 L372 126.5 L378 128.3 L384 130.1 L390 131.8 L396 133.3 L402 134.7 L408 135.7 L414 136.5 L420 136.9 L426 137.0 L432 136.7 L438 136.1 L444 135.1 L450 133.9 L456 132.4 L462 130.7 L468 129.0 L474 127.2 L480 125.4 L486 123.7 L492 122.3 L498 121.0 L504 120.0 L510 119.3 L516 119.0 L522 119.1 L528 119.5 L534 120.2 L540 121.2 L546 122.6" stroke="url(#mf-cw)" stroke-width="3.5"/><path d="M36 119.6 L42 119.1 L48 119.0 L54 119.2 L60 119.8 L66 120.7 L72 121.9 L78 123.4 L84 125.0 L90 126.7 L96 128.5 L102 130.3 L108 132.0 L114 133.5 L120 134.8 L126 135.8 L132 136.6 L138 136.9 L144 137.0 L150 136.6 L156 136.0 L162 135.0 L168 133.7 L174 132.2 L180 130.5 L186 128.7 L192 127.0 L198 125.2 L204 123.6 L210 122.1 L216 120.9 L222 119.9 L228 119.3 L234 119.0 L240 119.1 L246 119.5 L252 120.3 L258 121.4 L264 122.7 L270 124.3 L276 126.0 L282 127.8 L288 129.6 L294 131.3 L300 132.9 L306 134.3 L312 135.5 L318 136.3 L324 136.8 L330 137.0 L336 136.8 L342 136.3 L348 135.4 L354 134.2 L360 132.8 L366 131.2 L372 129.5 L378 127.7 L384 125.9 L390 124.2 L396 122.7 L402 121.3 L408 120.3 L414 119.5 L420 119.1 L426 119.0 L432 119.3 L438 119.9 L444 120.9 L450 122.1 L456 123.6 L462 125.3 L468 127.0 L474 128.8 L480 130.6 L486 132.3 L492 133.7 L498 135.0 L504 136.0 L510 136.7 L516 137.0 L522 136.9 L528 136.5 L534 135.8 L540 134.8 L546 133.4" stroke="url(#mf-cw)" stroke-width="3.5"/><path d="M85.2 118L103.2 138M85.2 138L103.2 118M179.5 118L197.5 138M179.5 138L197.5 118M273.7 118L291.7 138M273.7 138L291.7 118M368.0 118L386.0 138M368.0 138L386.0 118M462.2 118L480.2 138M462.2 138L480.2 118" stroke="url(#mf-cw)" stroke-width="3"/></g></g></symbol></defs></svg>'


def logo_svg(cls):
    return f'<svg class="{cls}" viewBox="{LOGO_VB}" role="img" aria-label="{e(C["brand"])}"><use href="#mf-logo"/></svg>'


# ---------------------------------------------------------------- chrome stickers on the computer
# Each design is a list of (svg element with FILL placeholder, fill). "main" = the sticker's chrome finish.
_DESIGNS = {
    "heart": [('<path d="M50 88C20 66 7 48 7 31 7 17 18 8 31 8c9 0 15 5 19 12 4-7 10-12 19-12 13 0 24 9 24 23 0 17-13 35-43 57Z"/>', "main")],
    "star": [('<path d="M50 5l11.5 31.5H95L68 57l10 34-28-20-28 20 10-34L5 36.5h33.5Z"/>', "main")],
    "bolt": [('<path d="M60 3 18 57h28l-9 40 46-58H55Z"/>', "main")],
    "skull": [('<path d="M50 16c-22 0-35 15-35 33 0 12 6 21 14 25v10c0 4 3 7 7 7h28c4 0 7-3 7-7V74c8-4 14-13 14-25 0-18-13-33-35-33Z"/>', "main"),
              ('<path d="M74 14l-14-10v20Zm0 0 14-10v20Z"/><circle cx="74" cy="14" r="5"/>', "url(#chromePink)")],
    "butterfly": [('<path d="M49 50C40 18 8 8 8 33c0 14 18 20 41 17ZM51 50c9-32 41-42 41-17 0 14-18 20-41 17ZM49 52C30 52 14 62 20 78c6 14 24 4 29-26ZM51 52c19 0 35 10 29 26-6 14-24 4-29-26Z"/>', "main")],
    "lips": [('<path d="M6 50c12-16 26-22 44-11 18-11 32-5 44 11-12 20-28 30-44 30S18 70 6 50Z"/>', "main")],
    "bow": [('<path d="M50 48 12 24c-8 10-8 38 0 48ZM50 48l38-24c8 10 8 38 0 48ZM44 56l-12 34 12-6 6 10 6-10 12 6-12-34Z"/><circle cx="50" cy="50" r="11"/>', "main")],
    "cherry": [('<circle cx="32" cy="72" r="17"/><circle cx="68" cy="76" r="17"/>', "url(#chromeRed)"),
               ('<path d="M62 10q22-10 30 6-18 6-30-6Z"/>', "url(#chromeGreen)")],
    "polish": [('<rect x="38" y="6" width="24" height="30" rx="4"/>', "url(#chromeBlack)"),
               ('<rect x="41" y="34" width="18" height="10"/><rect x="22" y="42" width="56" height="50" rx="14"/>', "main")],
}
_DETAILS = {   # drawn on top, no die-cut
    "skull": '<circle cx="37" cy="52" r="8" fill="#1c1a1e"/><circle cx="63" cy="52" r="8" fill="#1c1a1e"/><path d="M50 60l-4 8h8Z" fill="#1c1a1e"/><path d="M40 84v-8M50 84v-8M60 84v-8" stroke="#1c1a1e" stroke-width="2.5"/>',
    "butterfly": '<path d="M50 32v44" stroke="#1c1a1e" stroke-width="4" stroke-linecap="round"/>',
    "lips": '<path d="M12 50q38 10 76 0" stroke="#5a1636" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "cherry": '<path d="M32 55q4-30 30-45M68 59q-8-28-6-49" stroke="#3b5d1f" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "polish": '<text x="50" y="74" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-size="15" fill="#fff" opacity=".85">mf</text>',
}
_N = [0]


def sticker(design, fill, x, y, size, rot):
    _N[0] += 1
    cid = f"sk{_N[0]}"
    if not fill.startswith("url(") and fill != "main":
        fill = f"url(#{fill})"
    parts = _DESIGNS[design]
    shapes = "".join(el for el, _ in parts)
    body = "".join(f'<g fill="{fill if f == "main" else f}" stroke="#4d4a5a" stroke-width="1.2">{el}</g>' for el, f in parts)
    return (f'<svg class="stk" viewBox="0 0 100 100" style="left:{x}px;top:{y}px;width:{size}px;transform:rotate({rot}deg)" aria-hidden="true">'
            f'<defs><clipPath id="{cid}">{shapes}</clipPath></defs>'
            f'<g fill="#000" opacity=".18" transform="translate(2 3)" stroke="#000" stroke-width="13" stroke-linejoin="round">{shapes}</g>'
            f'<g fill="#fff" stroke="#fff" stroke-width="12" stroke-linejoin="round">{shapes}</g>'
            f'{body}{_DETAILS.get(design, "")}'
            f'<g clip-path="url(#{cid})"><rect x="-60" y="-20" width="70" height="140" fill="url(#sheen)" transform="rotate(25 50 50)"><animate attributeName="x" values="-90;130;130" keyTimes="0;.45;1" dur="4.5s" begin="{(_N[0] % 7) * 0.6:.1f}s" repeatCount="indefinite"/></rect>'
            f'<ellipse cx="32" cy="26" rx="15" ry="6" fill="#fff" opacity=".7" transform="rotate(-30 32 26)"/></g></svg>')


def word_sticker(text, fill, x, y, width, rot):
    t = e(text)
    txt = f'<text x="80" y="38" text-anchor="middle" font-family="Bagel Fat One,Arial Black,Arial,sans-serif" font-size="36">{t}</text>'
    return (f'<svg class="stk" viewBox="0 0 160 56" style="left:{x}px;top:{y}px;width:{width}px;transform:rotate({rot}deg)" aria-hidden="true">'
            f'<g fill="#000" opacity=".18" stroke="#000" stroke-width="13" stroke-linejoin="round" transform="translate(2 3)">{txt}</g>'
            f'<g fill="#fff" stroke="#fff" stroke-width="12" stroke-linejoin="round">{txt}</g>'
            f'<g fill="{fill}" stroke="#3a1a2c" stroke-width="1.2">{txt}</g></svg>')


def name_sticker(x, y, rot):
    return word_sticker(C["owner"].split()[0].lower() + " x", "url(#chromePink)", x, y, 118, rot)


CHROME_DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<linearGradient id="chrome" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".32" stop-color="#d8d8e6"/><stop offset=".48" stop-color="#85859c"/><stop offset=".53" stop-color="#f6f6ff"/><stop offset=".78" stop-color="#b4b4c8"/><stop offset="1" stop-color="#6c6c82"/></linearGradient>
<linearGradient id="chromePink" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#fff2f9"/><stop offset=".32" stop-color="#ffb3d9"/><stop offset=".48" stop-color="#c23f7c"/><stop offset=".53" stop-color="#ffe3f1"/><stop offset=".78" stop-color="#ff86c3"/><stop offset="1" stop-color="#9c2c5c"/></linearGradient>
<linearGradient id="chromeHolo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".2" stop-color="#d7c6ff"/><stop offset=".38" stop-color="#8a6cd8"/><stop offset=".5" stop-color="#c9fff0"/><stop offset=".66" stop-color="#ffc2e6"/><stop offset=".82" stop-color="#9ad8ff"/><stop offset="1" stop-color="#6d58b0"/></linearGradient>
<linearGradient id="chromeBlack" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#8b8796"/><stop offset=".45" stop-color="#2a2630"/><stop offset=".52" stop-color="#050406"/><stop offset=".58" stop-color="#6d6878"/><stop offset="1" stop-color="#141117"/></linearGradient>
<linearGradient id="chromeRed" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#ffd0dc"/><stop offset=".4" stop-color="#ff3d6e"/><stop offset=".52" stop-color="#8f0f33"/><stop offset=".6" stop-color="#ff8aa8"/><stop offset="1" stop-color="#a3123c"/></linearGradient>
<linearGradient id="chromeGreen" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#eaffd0"/><stop offset=".5" stop-color="#6fbf3a"/><stop offset="1" stop-color="#2f6a18"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs></svg>"""


def front_stickers():
    return (name_sticker(190, 364, -4) + sticker("heart", "chromePink", 404, 352, 54, 10))


def left_stickers():
    return sticker("cherry", "main", 110, 150, 86, -8)


def side_stickers():
    return sticker("butterfly", "chromeHolo", 90, 120, 100, -10) + sticker("lips", "chromePink", 120, 280, 74, 8)


def back_stickers():
    return sticker("bow", "chromePink", 40, 30, 90, -12) + name_sticker(190, 150, 4)



# ---- Customise your avatar: clickable parts of her turnaround, each opening the services for that part
AVATAR_PARTS = [
    # key, label, hotspot box on the front view as % (left, top, width, height), services as (category, service slug)
    ("hair", "Hair", (36.8, 2.3, 32.9, 6.2), [("hair", "cuts-and-styling"), ("hair", "colour"), ("hair", "extensions")]),
    ("eyes", "Lashes & brows", (42.1, 11.4, 17.1, 1.5), [("beauty", "lashes"), ("beauty", "brows")]),
    ("nose", "Piercing", (47.9, 13.2, 4.7, 2), [("piercing", "nose-piercing"), ("piercing", "ear-piercing"), ("piercing", "navel-piercing")]),
    ("ear", "Piercing", (35.5, 11.2, 4.5, 3.7), [("piercing", "ear-piercing"), ("piercing", "nose-piercing"), ("piercing", "navel-piercing")]),
    ("lips", "Lips", (46.1, 15.2, 9.2, 1.5), [("filler", "lip-filler")]),
    ("face", "Face", (40.8, 8.9, 20.3, 8.9), [("beauty", "makeup"), ("filler", "dermal-filler"), ("beauty", "waxing")]),
    ("navel", "Piercing", (45.3, 38.7, 10.5, 3.5), [("piercing", "navel-piercing"), ("piercing", "ear-piercing"), ("piercing", "nose-piercing")]),
    ("hand-l", "Nails", (3.9, 45.7, 11, 11), [("nails", "gel-nails"), ("nails", "biab"), ("nails", "acrylic-nails"), ("nails", "nail-art")]),
    ("hand-r", "Nails", (84.2, 45.7, 13.2, 11), [("nails", "gel-nails"), ("nails", "biab"), ("nails", "acrylic-nails"), ("nails", "nail-art")]),
]


def customiser():
    svc = {(c["slug"], sv["slug"]): (c, sv) for c in CATEGORIES for sv in c["services"]}
    spots, panels, chips, seen = "", "", "", set()
    for key, label, (x, y, w, h), items in AVATAR_PARTS:
        group = label.lower().replace(" & ", "-").replace(" ", "-")
        spots += (f'<button type="button" class="hs hs-{key}" data-part="{group}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%" '
                  f'aria-label="Customise: {e(label)}"><span class="hs-dot" aria-hidden="true"></span><span class="hs-tip">{e(label)}</span></button>')
        if group in seen:
            continue
        seen.add(group)
        chips += f'<button type="button" class="cz-chip" data-part="{group}">{e(label)}</button>'
        rows = ""
        for cat, slug in items:
            c, sv = svc[(cat, slug)]
            rows += (f'<li><a href="{c["slug"]}/{sv["slug"]}/"><span class="pk"></span><b>{e(sv["name"])}</b>'
                     f'<small>{e(sv["short"])}</small><em>{from_price(sv)}</em></a></li>')
        panels += (f'<section class="cz-part" data-part="{group}" hidden><h3>{e(label)}</h3><ul class="cz-list">{rows}</ul>'
                   f'<p class="cz-actions"><a class="cz-book" href="{e(C["booking_url"])}"><span class="pk"></span>Book this</a>'
                   f'<button type="button" class="cz-reset">&larr; pick another part</button></p></section>')
    return (f'<div class="cz"><div class="addr">Address <span>{e(C["site_url"])}/customise</span></div>'
            f'<div class="cz-main"><div class="cz-stage"><p class="cz-hud">CUSTOMISE YOUR AVATAR</p>'
            f'<div class="cz-fig" id="czFig" role="img" aria-label="{e(C["owner"])}\'s avatar: black and pink hair, studded denim vest, cargo trousers">{spots}</div>'
            f'<div class="cz-rot"><button type="button" class="cz-turn" data-d="-1" aria-label="Turn left">&#9664;</button>'
            f'<span>drag to turn</span><button type="button" class="cz-turn" data-d="1" aria-label="Turn right">&#9654;</button></div></div>'
            f'<aside class="cz-panel" aria-live="polite"><section class="cz-part cz-intro" data-part="" ><h3>Pick a part</h3>'
            f'<p>Click part of her to customise it, or choose below.</p><div class="cz-chips">{chips}</div></section>{panels}</aside></div></div>')


def desktop():
    """The computer's desktop: app icons, pop-up windows and a taskbar."""
    apps = [("avatar", "Customise", "her", "services/", customiser()),
            ("web", "myface.com", "web", "./", f'<div class="addr">Address <span>{e(C["site_url"])}/~{e(C["owner"].split()[0].lower())}</span></div>' + myspace())]
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
                 '<div class="spin"><button type="button" class="avatar-btn" id="avatarBtn" aria-label="Spin the MyFace mascot">'
                 '<span class="mascot" id="mascot" role="img" aria-label="The MyFace mascot: an emo girl with black and pink hair"></span></button>'
                 '<p class="bubble" id="bubble" aria-live="polite">hiya! welcome to myface x</p><p class="rot-hint" aria-hidden="true">&larr; drag to turn &rarr;</p></div>'))
    apps.append(("about", "About", "about", "about/",
                 f'<p>{e(C["brand"])} is {e(C["owner"])}\'s home beauty studio in {e(C["town"])} for hair, nails, lashes, brows, piercing and lip filler.</p>'
                 f'<p>[A line or two about you.]</p><p class="win-foot"><a href="about/">More about me &rarr;</a></p>'))
    apps.append(("contact", "Contact", "contact", "contact/",
                 f'<ul class="plain"><li><a href="tel:{e(C["phone"])}">{e(C["phone"])}</a></li><li><a href="mailto:{e(C["email"])}">{e(C["email"])}</a></li>'
                 f'<li><a href="{e(C["instagram"])}">Instagram</a></li></ul><p class="win-foot"><a href="contact/">Contact page &rarr;</a></p>'))
    icons = "".join(f'<li><a class="app" href="{e(href)}" data-app="{k}">{icon(ic)}<span>{e(label)}</span></a></li>' for k, label, ic, href, _ in apps)
    wins = "".join(f'<section class="win app-win{" web" if k == "web" else ""}" id="win-{k}" data-label="{e(label)}" hidden aria-label="{e(label)}">'
                   f'<div class="titlebar"><button type="button" class="back wback">&larr; Back</button><span class="tpath">{e(label)}</span><span class="wctl"><button type="button" class="min" aria-label="Minimise {e(label)}">_</button><button type="button" class="max" aria-label="Maximise {e(label)}">&#9633;</button><button type="button" class="close" aria-label="Close {e(label)}">&times;</button></span></div>'
                   f'<div class="win-body">{body}</div></section>' for k, label, ic, href, body in apps)
    menu = "".join(f'<li><a href="{e(href)}" data-app="{k}">{icon(ic, "mic")}{e(label)}</a></li>' for k, label, ic, href, _ in apps)
    menu += "".join(f'<li><a href="{h}">{icon(ic, "mic")}{n}</a></li>' for n, h, ic in
                    [("All treatments", "services/", "nails"), ("Aftercare", "aftercare/", "beauty"), ("FAQ", "faq/", "about"), ("Areas", "areas/", "web"), ("Gallery", "gallery/", "her")])
    return f"""<div class="os" id="os">
<div class="wall" aria-hidden="true"><svg class="wall-logo" viewBox="{LOGO_VB}"><use href="#mf-logo"/></svg></div>
<ul class="apps">{icons}</ul>
{wins}
<nav class="startmenu" id="startmenu" hidden aria-label="Start menu"><p class="sm-head">{e(C["brand"])} 95</p><ul>{menu}<li class="sm-sep"><button type="button" class="logoff-btn">&#9211; Log off</button></li></ul></nav>
<div class="taskbar"><button type="button" class="start" id="startBtn" aria-expanded="false" aria-controls="startmenu"><svg class="start-logo" viewBox="{LOGO_VB}" aria-hidden="true"><use href="#mf-logo"/></svg>Start</button><div class="tasks" id="tasks" aria-label="Open windows"></div><div class="tray"><svg class="mic" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 9a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/></svg><svg class="mic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4zM16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg><span id="clock">--:--</span><button type="button" class="tray-off logoff-btn" aria-label="Log off"><svg class="mic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v8M6.3 6.3a8 8 0 1 0 11.4 0"/></svg></button></div></div>
</div>"""


def computer():
    keys = "".join('<i></i>' for _ in range(56))
    box = '<div class="f fr"></div><div class="f bk"></div><div class="f lf"></div><div class="f rt"></div><div class="f tp"></div><div class="f bt"></div>'
    return f"""<div class="captcha-intro" id="captcha" role="dialog" aria-modal="true" aria-labelledby="capLabel">
<div class="cap-box">
<div class="cap-top">
<svg class="cap-img" viewBox="0 0 520 170" role="img" aria-label="myface, written captcha-style in mixed warped letters">
<rect width="520" height="170" fill="url(#mf-stripes)"/><rect width="520" height="170" fill="url(#mf-dots)" opacity=".8"/>
<g stroke="#9a96a3" stroke-width="1.5" fill="none" opacity=".8"><path d="M0 40 L520 70"/><path d="M0 140 L520 110"/><path d="M60 0 L140 170"/><path d="M380 0 L330 170"/></g><g filter="url(#mf-wob-big)" id="capLetters"><use href="#mf-letters" width="520" height="170"/></g><path d="M6 104 C 90 52, 170 150, 270 96 S 430 58, 514 92" fill="none" stroke="#2a2630" stroke-width="4"/><path d="M10 66 Q 200 132 300 70 T 512 120" fill="none" stroke="#d23c86" stroke-width="2.5"/>
</svg>
<div class="cap-tools"><button type="button" class="cap-ico" id="capShuffle" aria-label="New captcha"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.3-5.6M20 4v5h-5"/></svg></button><button type="button" class="cap-ico" id="capAudio" aria-label="Hear the captcha"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4zM16 9a4 4 0 0 1 0 6"/></svg></button></div>
</div>
<div class="cap-row">
<button type="button" class="cap-check" id="capCheck" role="checkbox" aria-checked="false" aria-labelledby="capLabel"><span class="cap-spin" aria-hidden="true"></span><svg class="cap-tick" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6"/></svg></button>
<span id="capLabel">I'm not a robot</span>
<span class="cap-brand">customise<br>your avatar</span>
</div>
</div>
<a class="cap-skip" href="#content" id="capSkip">skip intro</a>
</div>
<main id="content" class="room">
{CHROME_DEFS}
<div class="scene" id="scene">
<div class="pop95" id="avatarPop" role="alertdialog" aria-labelledby="popT" aria-describedby="popD" hidden><div class="pop-bar"><span id="popT">avatar.exe</span><button type="button" class="pop-x" aria-label="Close">&times;</button></div><div class="pop-body"><svg class="pop-ic" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3 30 28H2z" fill="#ffd23f" stroke="#000" stroke-width="2" stroke-linejoin="round"/><path d="M16 11v9" stroke="#000" stroke-width="3" stroke-linecap="round"/><circle cx="16" cy="24" r="1.8"/></svg><p id="popD"><b>Your avatar needs customising!</b>Click the computer to customise your avatar and find your treatment x</p></div><div class="pop-btns"><button type="button" class="pop-go">Customise</button><button type="button" class="pop-ok">OK</button></div></div>
<div class="bands" aria-hidden="true"><div class="band b1"><div class="track"><p><span>NAILS</span><i>&#9632;</i> <span>PIERCING</span><i>&#9632;</i> <span>HAIR</span><i>&#9632;</i> <span>MAKEUP</span><i>&#9632;</i> <span>LASHES</span><i>&#9632;</i> <span>BROWS</span><i>&#9632;</i> <span>LIP FILLER</span><i>&#9632;</i></p><p><span>NAILS</span><i>&#9632;</i> <span>PIERCING</span><i>&#9632;</i> <span>HAIR</span><i>&#9632;</i> <span>MAKEUP</span><i>&#9632;</i> <span>LASHES</span><i>&#9632;</i> <span>BROWS</span><i>&#9632;</i> <span>LIP FILLER</span><i>&#9632;</i></p></div></div><div class="band b2"><div class="track"><p><span>HOME BEAUTY SPECIALIST</span><i>&#9632;</i> <span>MANCHESTER</span><i>&#9632;</i> <span>HOME BEAUTY SPECIALIST</span><i>&#9632;</i> <span>MANCHESTER</span><i>&#9632;</i></p><p><span>HOME BEAUTY SPECIALIST</span><i>&#9632;</i> <span>MANCHESTER</span><i>&#9632;</i> <span>HOME BEAUTY SPECIALIST</span><i>&#9632;</i> <span>MANCHESTER</span><i>&#9632;</i></p></div></div><div class="band b3"><div class="track"><p><span>ELLA MOORE</span><i>&#9632;</i> <span>CUSTOMISE YOUR AVATAR</span><i>&#9632;</i> <span>ELLA MOORE</span><i>&#9632;</i> <span>CUSTOMISE YOUR AVATAR</span><i>&#9632;</i></p><p><span>ELLA MOORE</span><i>&#9632;</i> <span>CUSTOMISE YOUR AVATAR</span><i>&#9632;</i> <span>ELLA MOORE</span><i>&#9632;</i> <span>CUSTOMISE YOUR AVATAR</span><i>&#9632;</i></p></div></div></div>
<div class="deck3d" id="deck3d"></div>
<div class="rig" id="rig">
<div class="monitor box">
<div class="f fr front"><div class="screen" id="screen">{desktop()}<span class="glare"></span></div>
{front_stickers()}<button type="button" class="zoom-btn" id="zoomBtn" aria-label="Zoom into the computer screen"></button></div>
<div class="f bk"></div><div class="f lf">{left_stickers()}</div><div class="f rt">{side_stickers()}</div><div class="f tp"></div><div class="f bt"></div>
</div>
<div class="shell s-top"></div><div class="shell s-bot"></div><div class="shell s-left"></div><div class="shell s-right"></div>
<div class="shell s-rear"><span class="vents"></span>{back_stickers()}</div>
<div class="neck box">{box}</div>
<div class="base3d box">{box}</div>
<div class="kbd box"><div class="f fr"></div><div class="f bk"></div><div class="f lf"></div><div class="f rt"></div><div class="f tp keys">{keys}</div><div class="f bt"></div></div>
<div class="shadow"></div>
</div>
</div>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"}}}}</script>
<script type="module">import {{ createDeck }} from './assets/deck.js?v=56';
try {{ window.MFDeck = createDeck(document.getElementById('deck3d'), {{ phone: matchMedia('(max-width: 620px)').matches && /[?&]phone\b/.test(location.search) }}); window.dispatchEvent(new Event('mfdeck')); }} catch (e) {{ console.warn('3D computer unavailable', e); }}</script>
</div>
<div class="zoomview" id="zoomview" hidden><div class="zv-mon" id="zvMon"><div class="zv-screen" id="zvScreen"><span class="glare"></span></div></div>
</div>
<div class="caption">
<p class="cap-tag">{e(C['tagline'])}</p>
<h1>Hair, nails, lashes, piercing &amp; lip filler in {e(C['town'])}</h1>
<p>An appointment-only home beauty studio in {e(C['town'])}, also covering Droylsden, Oldham, Stockport and the surrounding areas.</p>
</div>
</main>"""


# ---------------------------------------------------------------- build
def build():
    for f in os.listdir(OUT):
        p = os.path.join(OUT, f)
        if os.path.isdir(p) and f not in ("assets", ".git", ".github", "deck-lab") and os.path.exists(os.path.join(p, "index.html")):
            shutil.rmtree(p)
    town, city = C["town"], C["city"]

    page("", f"{C['brand']} | Nails, Hair, Lashes, Piercing & Lip Filler in {town}",
         f"{C['brand']} is an appointment-only home beauty studio in {town}, also covering Droylsden, Oldham and Stockport: gel and acrylic nails, BIAB, lashes, brows, hair, ear and nose piercing, and lip filler.",
         "", computer(), priority="1.0", home=True)

    page("services/", f"Treatments in {town} | {C['brand']}",
         f"All nail, hair, lash, brow, piercing and filler treatments at {C['brand']}, a home beauty studio in {town}.",
         "All treatments",
         "".join(sec(f'<a href="../{c["slug"]}/">{e(c["name"])}</a>', links(1, [(s["name"], from_price(s), f'{c["slug"]}/{s["slug"]}/') for s in c["services"]])) for c in CATEGORIES) + cta(1),
         crumbs=[("Treatments", "services/")], priority="0.9")

    for c in CATEGORIES:
        cp = f'{c["slug"]}/'
        page(cp, f"{c['name']} in {town} | {C['brand']}",
             f"{c['blurb']} at {C['brand']}, a home studio in {town}. " + " ".join(s["short"] for s in c["services"])[:90],
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
            page(sp, f"{s['name']} in {town} | {C['brand']}",
                 f"{s['name']} in {town}, {from_price(s)}. {s['short']} Appointment-only home studio in Manchester.",
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
         f"Prices for nails, hair, lashes, brows, waxing, piercing and lip filler at {C['brand']} in {town}.",
         "Price list", rows + "<p class=\"note\">Prices are a guide and are confirmed at booking.</p>" + cta(1),
         crumbs=[("Prices", "prices/")], priority="0.8")

    page("areas/", f"Areas Covered | {C['brand']}", f"{C['brand']} is a home beauty studio in {town}, also covering Droylsden, Oldham, Stockport and the surrounding areas.",
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
         + sec("Where to find us", f"<p>{C['brand']} is a home studio in {town}. It's appointment-only with no walk-ins, and the full address is sent once you've booked.</p><p>Also covering <a href=\"../areas/droylsden/\">Droylsden</a>, <a href=\"../areas/oldham/\">Oldham</a> and <a href=\"../areas/stockport/\">Stockport</a>.</p>"),
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
    with open(os.path.join(OUT, "assets", "search.json"), "w") as f:
        json.dump(SEARCH, f, separators=(",", ":"))
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {C['site_url']}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages + 404, sitemap.xml and robots.txt")


if __name__ == "__main__":
    build()
