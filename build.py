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
    "owner": "[YOUR NAME]",
    "town": "[TOWN]",
    "area": "[AREA / COUNTY]",
    "address": "[STREET ADDRESS]",
    "postcode": "[POSTCODE]",
    "phone": "[PHONE NUMBER]",
    "email": "[EMAIL]",
    "instagram": "https://www.instagram.com/[HANDLE]",
    "booking_url": "[BOOKING LINK]",       # e.g. your Fresha / Booksy / Square link
    "hours": [("Mon – Fri", "[TIMES]"), ("Saturday", "[TIMES]"), ("Sunday", "[TIMES]")],
}
C = CONFIG
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- content
# Each category has its own page; each service has a page inside it.
CATEGORIES = [
    {
        "slug": "hair", "name": "Hair",
        "blurb": "Cuts, colour, styling and extensions",
        "intro": f"<p>Whether it's a tidy-up, a full change of colour or extra length and volume, hair appointments at {C['brand']} start with a proper chat about what you want and what will suit your hair.</p>",
        "services": [
            {"slug": "cuts-and-styling", "name": "Haircuts & Styling",
             "short": "Cuts, restyles and blow-dries for all hair types.",
             "intro": "<p>From a trim to keep your ends healthy to a complete restyle, every cut starts with a consultation so we agree on the shape, length and how you style it day to day.</p><p>Blow-dries and occasion styling are available on their own, too, for nights out, weddings and photos.</p>",
             "expect": ["A consultation about the look you want and your routine", "Wash and condition", "Cut and finish, with tips for styling it at home"],
             "time": "[TIME]",
             "faqs": [("How often should I get a trim?", "Most people book every 6–12 weeks depending on length and style. Shorter, sharper cuts need trimming more often to keep their shape."),
                      ("Can I bring a picture?", "Yes, please do. Pictures are the easiest way to show the look you're after.")]},
            {"slug": "colour", "name": "Hair Colour",
             "short": "Full colour, roots, highlights, balayage and toners.",
             "intro": "<p>Colour services include root touch-ups, all-over colour, highlights, balayage and toners. Bigger changes, like going much lighter, may take more than one appointment to keep your hair in good condition.</p>",
             "expect": ["A colour consultation and strand check", "A skin patch test at least 48 hours before your appointment", "Colour, tone, wash and finish"],
             "time": "[TIME]",
             "faqs": [("Do I need a patch test?", "Yes. A skin patch test is needed at least 48 hours before any colour service, even if you've had colour before, because allergies can develop over time."),
                      ("Can you take me from dark to blonde in one go?", "Sometimes, but often it's safer done over a few sessions. We'll be honest at your consultation about what's realistic for your hair.")]},
            {"slug": "extensions", "name": "Hair Extensions",
             "short": "Added length and volume with [METHOD] extensions.",
             "intro": "<p>Extensions add length, thickness or a pop of colour. We'll match the shade and texture to your own hair and talk you through how to look after them.</p>",
             "expect": ["Consultation and colour match", "Fitting by [METHOD]", "Blending cut and styling"],
             "time": "[TIME]",
             "faqs": [("How long do extensions last?", "It depends on the method and how you look after them. We'll explain maintenance and refit times for the type you choose."),
                      ("Will they damage my hair?", "Fitted and removed properly, and looked after at home, extensions shouldn't cause damage. Never remove them yourself.")]},
        ],
    },
    {
        "slug": "nails", "name": "Nails",
        "blurb": "Gel, BIAB, acrylics and nail art",
        "intro": f"<p>Nails are where {C['brand']} gets to play: clean natural sets, long sculpted acrylics, chrome, charms and full hand-painted art.</p>",
        "services": [
            {"slug": "gel-nails", "name": "Gel Nails",
             "short": "Gel polish on natural nails that lasts for weeks.",
             "intro": "<p>Gel polish is cured under a lamp, so it's dry the moment you leave and stays glossy without chipping. It's a good choice if you want colour on your natural nails without extensions.</p>",
             "expect": ["Nail prep, shaping and cuticle care", "Gel colour, cured under a lamp", "Top coat and cuticle oil"],
             "time": "[TIME]",
             "faqs": [("How long does gel polish last?", "Usually around 2–3 weeks, depending on how fast your nails grow and what you do with your hands."),
                      ("Should I peel it off?", "No. Peeling gel takes layers of your natural nail with it. Book a removal instead.")]},
            {"slug": "biab", "name": "BIAB Nails",
             "short": "Builder gel that strengthens your own nails.",
             "intro": "<p>BIAB (builder in a bottle) is a thicker builder gel applied over your natural nails. It adds strength, so it's popular with anyone trying to grow their nails out, and it can be infilled rather than fully removed each time.</p>",
             "expect": ["Prep and shaping", "Builder gel to strengthen and shape the nail", "Colour or natural finish"],
             "time": "[TIME]",
             "faqs": [("How often do I need an infill?", "Most people come back every 3–4 weeks."),
                      ("Can I have art on top?", "Yes, BIAB works well under colour, French tips, chrome and art.")]},
            {"slug": "acrylic-nails", "name": "Acrylic Nails",
             "short": "Sculpted extensions in any length and shape.",
             "intro": "<p>Acrylic extensions are built from liquid and powder to give you length and a strong shape: square, coffin, almond, stiletto, whatever you're into.</p>",
             "expect": ["Prep of the natural nail", "Tips or sculpting to your chosen length and shape", "Colour, art or charms to finish"],
             "time": "[TIME]",
             "faqs": [("How often do acrylics need infills?", "Usually every 2–3 weeks to keep them strong and balanced as your nails grow."),
                      ("What length can I go?", "Pretty much any. We'll talk through what's practical for your day-to-day.")]},
            {"slug": "nail-art", "name": "Nail Art",
             "short": "Hand-painted designs, chrome, gems and charms.",
             "intro": "<p>Bring a picture, a mood or just a colour, and we'll design something around it. Hand-painted art, chrome, 3D gel, gems and charms are all on the menu.</p>",
             "expect": ["A chat about the design", "Base set of your choice", "Art priced by detail"],
             "time": "Depends on the design",
             "faqs": [("Can I book nail art on its own?", "It's added to a gel, BIAB or acrylic set. Let us know the design when you book so enough time is set aside."),
                      ("How is art priced?", "By detail and how many nails, from simple accents to a full set.")]},
        ],
    },
    {
        "slug": "beauty", "name": "Beauty",
        "blurb": "Lashes, brows, waxing and make-up",
        "intro": f"<p>The finishing touches: lashes, brows, waxing and make-up for everyday or big occasions.</p>",
        "services": [
            {"slug": "lashes", "name": "Lash Lifts & Extensions",
             "short": "Lifted, tinted natural lashes or full extensions.",
             "intro": "<p>A lash lift curls your own lashes from the root and is usually paired with a tint, so they look longer and darker without mascara. Extensions add length and fullness lash by lash.</p>",
             "expect": ["A patch test before your first lift, tint or extensions", "Lift and tint, or extensions applied", "Aftercare advice to make them last"],
             "time": "[TIME]",
             "faqs": [("How long does a lash lift last?", "Usually around 6–8 weeks, as your lashes naturally shed and regrow."),
                      ("Do I need a patch test?", "Yes, at least 24–48 hours before your first appointment.")]},
            {"slug": "brows", "name": "Brows",
             "short": "Shaping, tinting and brow lamination.",
             "intro": "<p>Brow appointments include shaping with wax or threading, tinting and lamination, which sets your brow hairs in a brushed-up, fuller-looking shape.</p>",
             "expect": ["Brow mapping to suit your face", "Shape, tint or lamination", "A finishing brow gel"],
             "time": "[TIME]",
             "faqs": [("How long does brow lamination last?", "Usually around 6–8 weeks."),
                      ("Can I have a tint and lamination together?", "Yes, they're often booked together.")]},
            {"slug": "waxing", "name": "Waxing",
             "short": "Smooth results for face and body.",
             "intro": "<p>Quick, clean waxing for face and body. Hair needs to be a little grown out for wax to grip, roughly the length of a grain of rice.</p>",
             "expect": ["Skin prep", "Wax suited to the area", "Soothing aftercare"],
             "time": "[TIME]",
             "faqs": [("How long should my hair be?", "Around 0.5 cm, or about 2–3 weeks of growth after shaving."),
                      ("Can I wax if I use retinoids?", "Tell us at booking. Some skincare products make skin more sensitive to waxing.")]},
            {"slug": "makeup", "name": "Make-up",
             "short": "Make-up for nights out, events and shoots.",
             "intro": "<p>Make-up for birthdays, nights out, prom, weddings and shoots, from soft and natural to full glam.</p>",
             "expect": ["A chat about the look and your outfit", "Skin prep", "Full make-up, lashes optional"],
             "time": "[TIME]",
             "faqs": [("Do you do bridal make-up?", "[YES/NO — add details]"),
                      ("Should I come with a clean face?", "Yes, ideally moisturised but with no make-up on.")]},
        ],
    },
    {
        "slug": "piercing", "name": "Piercing",
        "blurb": "Ear, nose and body piercing",
        "intro": f"<p>Piercings at {C['brand']} are done by [PIERCER / QUALIFICATIONS] with [METHOD] in a clean, licensed space, with jewellery to choose from.</p><p>Age policy: [YOUR AGE POLICY]. Photo ID may be asked for.</p>",
        "services": [
            {"slug": "ear-piercing", "name": "Ear Piercing",
             "short": "Lobes, helix, tragus, conch and more.",
             "intro": "<p>From first lobes to curated ears: lobe, upper lobe, helix, forward helix, tragus, conch, daith and more. We'll help you plan placements that suit your ear shape.</p>",
             "expect": ["Choose your placement and jewellery", "Marking and a check in the mirror", "Piercing, then aftercare advice"],
             "time": "[TIME]",
             "faqs": [("How long do ear piercings take to heal?", "Lobes usually take around 6–8 weeks. Cartilage piercings like the helix or conch can take 6–12 months or more."),
                      ("When can I change the jewellery?", "Only once it's healed. Come back and we can check it and change it for you.")]},
            {"slug": "nose-piercing", "name": "Nose Piercing",
             "short": "Nostril and septum piercings.",
             "intro": "<p>Nostril and septum piercings, placed to suit your face, with jewellery to choose from.</p>",
             "expect": ["Choose placement and jewellery", "Marking and checking", "Piercing and aftercare advice"],
             "time": "[TIME]",
             "faqs": [("How long does a nose piercing take to heal?", "A nostril usually takes around 4–6 months, and a septum around 2–3 months, sometimes longer."),
                      ("Does it hurt?", "There's a quick, sharp pinch. Most people say it's over faster than they expected.")]},
            {"slug": "body-piercing", "name": "Body Piercing",
             "short": "Navel and other body piercings.",
             "intro": "<p>Navel and other body piercings: [LIST THE PIERCINGS YOU OFFER]. Some body piercings are only legal from 18, so photo ID will be checked.</p>",
             "expect": ["Consultation and anatomy check", "Choose jewellery", "Piercing and aftercare advice"],
             "time": "[TIME]",
             "faqs": [("How long does a navel piercing take to heal?", "Usually around 6–12 months."),
                      ("Can everyone get every piercing?", "Not always. Some depend on your anatomy, which we'll check before piercing.")]},
        ],
    },
    {
        "slug": "filler", "name": "Filler",
        "blurb": "Lip and dermal filler",
        "intro": f"<p>Filler treatments at {C['brand']} are carried out by [PRACTITIONER / QUALIFICATIONS], using hyaluronic acid fillers. Every treatment starts with a consultation and a medical history check.</p><p><strong>Over-18s only.</strong> It's illegal in England to give cosmetic filler to anyone under 18, and ID will be checked.</p>",
        "services": [
            {"slug": "lip-filler", "name": "Lip Filler",
             "short": "Subtle volume, shape and hydration for lips.",
             "intro": "<p>Lip filler adds volume, defines shape or balances the lips using a hyaluronic acid gel. Results can be kept subtle, and you can build up over more than one appointment.</p><p>Hyaluronic acid filler is temporary and gradually breaks down. Lip filler commonly lasts around 6 months, though it varies from person to person.</p>",
             "expect": ["Consultation, medical history and consent", "Numbing, then filler placed in small amounts", "Aftercare advice and a review appointment"],
             "time": "[TIME]",
             "faqs": [("How long does lip filler last?", "Often around 6 months, but it varies depending on the product, the amount and your body."),
                      ("Will I swell?", "Some swelling and bruising is normal for a few days. It settles, and your final result shows after about two weeks."),
                      ("Who can't have filler?", "Anyone under 18, and anyone pregnant or breastfeeding. Some medical conditions and medications also rule it out, which we'll check at consultation.")]},
            {"slug": "dermal-filler", "name": "Dermal Filler",
             "short": "[CHEEK / CHIN / JAW — the areas you treat].",
             "intro": "<p>Dermal filler can restore or add volume and contour to areas such as [AREAS YOU TREAT]. Everything is planned at a consultation so results look like you.</p><p>Hyaluronic acid filler is temporary. How long it lasts depends on the area and product, which we'll explain at consultation.</p>",
             "expect": ["Consultation, medical history and consent", "Treatment", "Aftercare advice and a review appointment"],
             "time": "[TIME]",
             "faqs": [("Is filler permanent?", "No. Hyaluronic acid fillers break down naturally over time."),
                      ("Are there risks?", "As with any injectable treatment, there are risks. Most side effects are mild, like swelling and bruising, and serious complications are rare. We'll go through them with you before treatment.")]},
        ],
    },
]

AFTERCARE = [
    {"slug": "piercing", "name": "Piercing Aftercare",
     "body": "<ul><li>Clean twice a day with sterile saline spray. No alcohol, tea tree or harsh soaps.</li><li>Don't twist or turn the jewellery, and try not to touch it except when cleaning, with clean hands.</li><li>Avoid sleeping on new ear piercings. A travel pillow helps.</li><li>Keep it out of pools, hot tubs, the sea and baths until it's healed.</li><li>Some redness, swelling and clear or whitish fluid is normal early on.</li><li>Don't take the jewellery out to change it until it's fully healed.</li><li>If you see spreading redness, heat, yellow or green discharge, or feel unwell, contact us and see a GP or pharmacist.</li></ul>"},
    {"slug": "filler", "name": "Filler Aftercare",
     "body": "<ul><li>Avoid touching or massaging the area for 24 hours unless you've been told to.</li><li>Skip make-up on the area for 12–24 hours.</li><li>Avoid alcohol, strenuous exercise, saunas and heat for 24–48 hours.</li><li>Swelling and bruising are normal and usually settle within a few days. A cold compress can help.</li><li>Your final result shows after around two weeks. Come back for your review appointment.</li><li><strong>Get help straight away</strong> if you notice severe or worsening pain, skin that turns white, blue or blotchy, or any changes to your vision. Contact us immediately, and call 999 or go to A&amp;E if you can't reach us.</li></ul>"},
    {"slug": "lashes-and-brows", "name": "Lash & Brow Aftercare",
     "body": "<ul><li>Keep lashes and brows dry for 24 hours after a lift, tint or lamination. No steam, saunas or swimming.</li><li>Avoid mascara and brow products for 24 hours.</li><li>For extensions, use oil-free products and brush them gently every day.</li><li>Don't pick or pull at extensions. Book a removal instead.</li></ul>"},
    {"slug": "nails", "name": "Nail Aftercare",
     "body": "<ul><li>Use cuticle oil daily to keep nails and skin healthy.</li><li>Wear gloves for cleaning and washing up.</li><li>Don't use your nails as tools for opening cans or scraping labels.</li><li>Never pick or peel off gel, BIAB or acrylics. Book a removal.</li><li>If a nail lifts or breaks, get in touch so we can fix it before water gets underneath.</li></ul>"},
]

GENERAL_FAQS = [
    ("How do I book?", f"Book online through our <a href=\"{C['booking_url']}\">booking page</a>, message us on Instagram or call {C['phone']}."),
    ("Do you take deposits?", "[YOUR DEPOSIT POLICY]"),
    ("What's your cancellation policy?", "[YOUR CANCELLATION POLICY]"),
    ("Do I need a patch test?", "Yes, for hair colour, lash and brow tints, lash lifts and lash extensions. Patch tests need to be done 24–48 hours before your appointment."),
    ("Is there an age limit?", "Filler is over-18s only by law in England. For piercings our policy is [YOUR AGE POLICY]. For other treatments, under-16s need a parent or guardian with them."),
    ("Where are you?", f"{C['address']}, {C['town']} {C['postcode']}."),
    ("How do I pay?", "[PAYMENT METHODS]"),
]

# ---------------------------------------------------------------- helpers
e = html.escape
PAGES = []  # (path, priority)


def rel(depth, target):
    """Relative link from a page at `depth` folders deep to a site path like 'nails/biab/'."""
    return ("../" * depth) + target if (depth or target) else "./"


def sidebar(d):
    svc = "".join(f'<tr><th scope="row"><a href="{rel(d, c["slug"] + "/")}">{e(c["name"])}</a></th><td>{e(c["blurb"])}</td></tr>' for c in CATEGORIES)
    hrs = "".join(f"<tr><th scope=\"row\">{e(a)}</th><td>{e(b)}</td></tr>" for a, b in C["hours"])
    return f"""<aside class="side">
<section class="box profile">
<p class="h1ish">{e(C['brand'])}</p>
<div class="prow"><span class="ph">[Profile photo]</span>
<ul class="pinfo"><li><em>"Hair, nails, face, piercings — all under one roof."</em></li><li>Hair &amp; Beauty</li><li>{e(C['town'])}, United Kingdom</li><li>Mood: <b class="lime">glowing</b></li><li class="online"><span></span>Taking bookings!</li></ul></div>
</section>
<section class="box"><h2 class="hd lime-bg">Contacting {e(C['brand'])}</h2>
<div class="cbtns"><a class="btn pri" href="{e(C['booking_url'])}">Book a slot</a><a class="btn" href="{rel(d, 'contact/')}">Send message</a><a class="btn" href="{e(C['instagram'])}">Add on Instagram</a><a class="btn" href="tel:{e(C['phone'])}">Call us</a></div></section>
<section class="box"><h2 class="hd">{e(C['brand'])}'s Services</h2><table>{svc}</table></section>
<section class="box"><h2 class="hd lime-bg">Opening Hours</h2><table>{hrs}<tr><th scope="row">Find us</th><td>{e(C['address'])}, {e(C['town'])}</td></tr></table></section>
<section class="box radio"><button type="button" id="radio" aria-label="Play">&#9654;</button><div><b class="lime">{e(C['brand'])} Radio</b><br><span id="np">Press play for salon vibes</span></div></section>
</aside>"""


def page(path, title, desc, h1, main, crumbs=(), schema=None, priority="0.6"):
    d = path.count("/")
    nav = [("Home", ""), ("Hair", "hair/"), ("Nails", "nails/"), ("Beauty", "beauty/"), ("Piercing", "piercing/"),
           ("Filler", "filler/"), ("Prices", "prices/"), ("Aftercare", "aftercare/"), ("FAQ", "faq/"), ("Contact", "contact/")]
    cur = ' aria-current="page"'
    navh = "".join(f'<a href="{rel(d, t)}"{cur if t == path else ""}>{n}</a>' for n, t in nav)
    url = C["site_url"] + "/" + path
    crumb_list = [("Home", "")] + list(crumbs)
    bc = ""
    if crumbs:
        bc = '<nav class="crumbs" aria-label="Breadcrumb">' + " &rsaquo; ".join(
            f'<a href="{rel(d, p)}">{e(n)}</a>' if p != path else f"<span>{e(n)}</span>" for n, p in crumb_list) + "</nav>"
    graphs = [business_schema()]
    if crumbs:
        graphs.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": C["site_url"] + "/" + p} for i, (n, p) in enumerate(crumb_list)]})
    graphs += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graphs}, ensure_ascii=False).replace("</", "<\\/")
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
<meta name="theme-color" content="#ff4fb3">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel(d, 'assets/style.css')}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="top">
<div class="wrap bar"><a class="logo" href="{rel(d, '')}">my<span>face</span></a><span class="tag">a place for faces</span>
<a class="btn lime-btn" href="{e(C['booking_url'])}">Book now</a></div>
<nav class="nav" aria-label="Main"><div class="wrap">{navh}</div></nav>
</header>
<div class="wrap layout">
{sidebar(d)}
<main id="content" class="main">
{bc}
<div class="box banner"><h1>{e(h1)}</h1></div>
{main}
</main>
</div>
<footer class="foot"><div class="wrap">
<nav aria-label="Footer"><a href="{rel(d, 'about/')}">About</a><a href="{rel(d, 'services/')}">All services</a><a href="{rel(d, 'gallery/')}">Gallery</a><a href="{rel(d, 'faq/')}">FAQ</a><a href="{rel(d, 'privacy/')}">Privacy</a><a href="{rel(d, 'terms/')}">Terms</a><a href="{rel(d, 'contact/')}">Contact</a></nav>
<p>{e(C['brand'])} · Hair, beauty, nails, piercing &amp; filler in {e(C['town'])}, {e(C['area'])}</p>
<p>&copy;2026 {e(C['brand'])}. All rights reserved.</p>
</div></footer>
<script src="{rel(d, 'assets/site.js')}" defer></script>
</body>
</html>
"""
    target = os.path.join(OUT, path, "index.html") if path else os.path.join(OUT, "index.html")
    if path == "404.html":
        target = os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(doc)
    if path != "404.html":
        PAGES.append((path, priority))


def business_schema():
    return {"@type": "BeautySalon", "@id": C["site_url"] + "/#business", "name": C["brand"], "url": C["site_url"] + "/",
            "telephone": C["phone"], "email": C["email"], "sameAs": [C["instagram"]],
            "address": {"@type": "PostalAddress", "streetAddress": C["address"], "addressLocality": C["town"],
                        "addressRegion": C["area"], "postalCode": C["postcode"], "addressCountry": "GB"}}


def box(title, body, lime=False, id_=None):
    i = f' id="{id_}"' if id_ else ""
    return f'<section class="box"{i}><h2 class="hd{" lime-bg" if lime else ""}">{title}</h2><div class="pad">{body}</div></section>'


def faq_html(faqs):
    return "".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faqs)


def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in faqs]}


def cards(d, items):
    return '<div class="top8">' + "".join(
        f'<a href="{rel(d, href)}"><span class="ph sq">[Photo]</span><b>{e(name)}</b><small>{e(sub)}</small></a>'
        for name, sub, href in items) + "</div>"


def cta(d):
    return f'<div class="box ctabox"><p>Ready to book?</p><a class="btn pri" href="{e(C["booking_url"])}">Book a slot</a><a class="btn" href="{rel(d, "contact/")}">Ask a question</a></div>'


# ---------------------------------------------------------------- build
def build():
    for f in os.listdir(OUT):
        p = os.path.join(OUT, f)
        if os.path.isdir(p) and f not in ("assets", ".git") and os.path.exists(os.path.join(p, "index.html")):
            shutil.rmtree(p)
    town = C["town"]
    all_services = [(s, c) for c in CATEGORIES for s in c["services"]]

    # Home
    top8 = [(s["name"], "£[PRICE]", f'{c["slug"]}/{s["slug"]}/') for s, c in all_services[:8]]
    page("", f"{C['brand']} | Hair, Beauty, Nails, Piercing & Filler in {town}",
         f"{C['brand']} is a hair and beauty salon in {town} offering haircuts, colour, gel and acrylic nails, lashes, brows, ear and nose piercing, and lip filler.",
         f"{C['brand']} is in your extended network",
         box(f"{C['brand']}'s Blurbs",
             f"<h3>About me:</h3><p>[A few lines about you: how long you've been doing this, where you trained, and what clients can expect.] {C['brand']} is a hair and beauty studio in {town}, {C['area']}, for hair, nails, lashes, brows, piercing and filler.</p>"
             "<h3>Who I'd like to meet:</h3><p>Anyone after a fresh set, a new colour, a little sparkle in their ear or a bit of lip. Walk in as you, walk out as more you.</p>")
         + box(f"{C['brand']}'s Top 8 <small>(treatments)</small>", cards(0, top8), lime=True)
         + box("Latest Blog Entries <small>[offers &amp; news]</small>",
               '<ul class="blog"><li><b class="lime">[OFFER]</b> e.g. new client discount on your first set of nails</li><li><b class="lime">[NEWS]</b> e.g. new piercing jewellery has landed</li><li><b class="lime">[PRICES]</b> <a href="prices/">see the full price list</a></li></ul>')
         + box(f"{C['brand']}'s Friends Comments",
               '<div class="comments">' + '<div class="cmt"><span class="ph av">[Pic]</span><div><b class="lime">[Client name]</b> <small>[date]</small><p>[Paste a real client review here]</p></div></div>' * 2 + '</div>', lime=True),
         priority="1.0")

    # All services
    page("services/", f"Treatments & Services | {C['brand']}, {town}",
         f"All hair, beauty, nail, piercing and filler treatments at {C['brand']} in {town}.",
         "All treatments",
         "".join(box(f'<a href="../{c["slug"]}/">{e(c["name"])}</a>', cards(1, [(s["name"], s["short"], f'{c["slug"]}/{s["slug"]}/') for s in c["services"]]), lime=i % 2 == 1)
                 for i, c in enumerate(CATEGORIES)) + cta(1),
         crumbs=[("Services", "services/")], priority="0.9")

    # Categories and services
    for c in CATEGORIES:
        cp = f'{c["slug"]}/'
        page(cp, f"{c['name']} in {town} | {c['blurb']} | {C['brand']}",
             f"{c['blurb']} at {C['brand']} in {town}. " + " ".join(s["short"] for s in c["services"])[:110],
             f"{c['name']} in {town}",
             box(f"About our {c['name'].lower()} treatments", c["intro"])
             + box(f"{c['name']} menu", cards(1, [(s["name"], s["short"], f'{cp}{s["slug"]}/') for s in c["services"]]), lime=True)
             + cta(1),
             crumbs=[(c["name"], cp)], priority="0.9",
             schema=[{"@type": "OfferCatalog", "name": f"{c['name']} at {C['brand']}",
                      "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}} for s in c["services"]]}])
        for s in c["services"]:
            sp = f'{cp}{s["slug"]}/'
            others = [(o["name"], o["short"], f'{cp}{o["slug"]}/') for o in c["services"] if o is not s]
            care = {"piercing": "piercing", "filler": "filler", "nails": "nails"}.get(c["slug"])
            if s["slug"] in ("lashes", "brows"):
                care = "lashes-and-brows"
            care_html = f'<p><a href="../../aftercare/{care}/">Read the {c["name"].lower() if care != "lashes-and-brows" else "lash &amp; brow"} aftercare guide</a></p>' if care else ""
            page(sp, f"{s['name']} in {town} | {C['brand']}",
                 f"{s['name']} at {C['brand']} in {town}. {s['short']} Book online today.",
                 f"{s['name']} in {town}",
                 box(f"About {s['name'].lower()}", s["intro"])
                 + box("What to expect", "<ol>" + "".join(f"<li>{x}</li>" for x in s["expect"]) + f"</ol><p><b class=\"lime\">Time:</b> {e(s['time'])} &nbsp; <b class=\"lime\">Price:</b> from £[PRICE] (<a href=\"../../prices/\">full price list</a>)</p>{care_html}", lime=True)
                 + box("FAQs", faq_html(s["faqs"]))
                 + (box(f"More {c['name'].lower()}", cards(2, others), lime=True) if others else "")
                 + cta(2),
                 crumbs=[(c["name"], cp), (s["name"], sp)], priority="0.8",
                 schema=[{"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["short"],
                          "provider": {"@id": C["site_url"] + "/#business"}, "areaServed": town}, faq_schema(s["faqs"])])

    # Prices
    rows = "".join(f'<h3><a href="../{c["slug"]}/">{e(c["name"])}</a></h3><table class="prices">' +
                   "".join(f'<tr><th scope="row"><a href="../{c["slug"]}/{s["slug"]}/">{e(s["name"])}</a></th><td>from £[PRICE]</td></tr>' for s in c["services"]) + "</table>"
                   for c in CATEGORIES)
    page("prices/", f"Price List | {C['brand']}, {town}", f"Prices for hair, nails, beauty, piercing and filler at {C['brand']} in {town}.",
         "Price list", box("Prices", rows + "<p><small>Prices are a guide and may change after your consultation.</small></p>") + cta(1),
         crumbs=[("Prices", "prices/")], priority="0.8")

    # Aftercare
    page("aftercare/", f"Aftercare Guides | {C['brand']}", f"Aftercare advice for piercings, filler, lashes, brows and nails from {C['brand']} in {town}.",
         "Aftercare guides", box("Look after your new look", cards(1, [(a["name"], "Read the guide", f'aftercare/{a["slug"]}/') for a in AFTERCARE])),
         crumbs=[("Aftercare", "aftercare/")], priority="0.6")
    for a in AFTERCARE:
        ap = f'aftercare/{a["slug"]}/'
        page(ap, f"{a['name']} | {C['brand']}", f"{a['name']}: how to look after your treatment from {C['brand']} in {town}.",
             a["name"], box(a["name"], a["body"] + "<p><small>This is general advice. If you're worried about anything, contact us or speak to a GP or pharmacist.</small></p>") + cta(2),
             crumbs=[("Aftercare", "aftercare/"), (a["name"], ap)], priority="0.5")

    # FAQ, about, gallery, contact, legal
    page("faq/", f"FAQs | {C['brand']}, {town}", f"Answers to common questions about booking, deposits, patch tests and age limits at {C['brand']}.",
         "Frequently asked questions", box("FAQs", faq_html(GENERAL_FAQS)) + cta(1),
         crumbs=[("FAQ", "faq/")], schema=[faq_schema(GENERAL_FAQS)], priority="0.6")
    page("about/", f"About {C['owner']} | {C['brand']}, {town}", f"Meet {C['owner']}, the face behind {C['brand']} in {town}.",
         f"About {C['owner']}", box("About me", "<p>[Your story: how you got into hair and beauty, your training and qualifications, and what makes an appointment with you different.]</p>")
         + box("Qualifications &amp; insurance", "<ul><li>[QUALIFICATION]</li><li>[QUALIFICATION]</li><li>[INSURANCE / LICENCE DETAILS]</li></ul>", lime=True) + cta(1),
         crumbs=[("About", "about/")], priority="0.5")
    page("gallery/", f"Gallery | {C['brand']}, {town}", f"Photos of hair, nails, lashes, piercings and more by {C['brand']} in {town}.",
         "Gallery", "".join(box(e(c["name"]), cards(1, [(s["name"], "", f'{c["slug"]}/{s["slug"]}/') for s in c["services"]]), lime=i % 2 == 1) for i, c in enumerate(CATEGORIES)),
         crumbs=[("Gallery", "gallery/")], priority="0.5")
    hrs = "".join(f"<tr><th scope=\"row\">{e(a)}</th><td>{e(b)}</td></tr>" for a, b in C["hours"])
    page("contact/", f"Contact & Find Us | {C['brand']}, {town}", f"Contact {C['brand']} in {town}: phone, email, Instagram, address and opening hours.",
         "Contact us", box("Get in touch", f'<ul><li><b class="lime">Book:</b> <a href="{e(C["booking_url"])}">online booking</a></li><li><b class="lime">Call:</b> <a href="tel:{e(C["phone"])}">{e(C["phone"])}</a></li><li><b class="lime">Email:</b> <a href="mailto:{e(C["email"])}">{e(C["email"])}</a></li><li><b class="lime">Instagram:</b> <a href="{e(C["instagram"])}">message us</a></li></ul>')
         + box("Find us", f'<p>{e(C["address"])}<br>{e(C["town"])}, {e(C["area"])}<br>{e(C["postcode"])}</p><div class="ph map">[Map embed]</div><table>{hrs}</table>', lime=True),
         crumbs=[("Contact", "contact/")], priority="0.7")
    page("privacy/", f"Privacy Policy | {C['brand']}", f"How {C['brand']} uses and protects your information.", "Privacy policy",
         box("Privacy", "<p>[Your privacy policy: what you collect (booking details, consultation and medical forms), why, how long you keep it, and how clients can ask for it or have it deleted under UK GDPR.]</p>"),
         crumbs=[("Privacy", "privacy/")], priority="0.2")
    page("terms/", f"Terms & Booking Policy | {C['brand']}", f"Booking, deposit and cancellation terms at {C['brand']}.", "Terms & booking policy",
         box("Terms", "<p>[Deposits, cancellations, late arrivals, refunds and redos.]</p>"), crumbs=[("Terms", "terms/")], priority="0.2")
    page("404.html", f"Page not found | {C['brand']}", "This page couldn't be found.", "Oops, this page has left the network",
         box("404", f'<p>That page doesn\'t exist. Try the <a href="{C["site_url"]}/">homepage</a> or the <a href="{C["site_url"]}/services/">treatments list</a>.</p>'))

    # sitemap + robots
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
