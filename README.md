# My Face

A retro profile-page style site for My Face, an appointment-only home beauty studio in Droylsden (hair, nails, lashes, piercing and filler).

## Editing

Every page is generated from `build.py`.

1. Fill in `CONFIG` at the top of `build.py`: the domain, name, town, address, phone, booking link and hours.
2. Edit treatments, FAQs and aftercare in `CATEGORIES`, `AFTERCARE` and `GENERAL_FAQS`.
3. Run `python3 build.py` to rebuild all the pages, `sitemap.xml` and `robots.txt`.

Styles live in `assets/style.css`. The homepage mascot is `assets/mascot.webp`: a sprite of 7 turnaround views that `assets/site.js` spins in the her.exe window.

Prices are estimates from typical local prices, so the owner should check them.

## What's built for SEO

- A homepage with a 3D CSS computer: click it to zoom in, boot up and use the desktop (treatment windows, her.exe, and a MySpace-style profile in the myface.com window). All links are real HTML for search engines
- Location pages for Droylsden, Manchester and Oldham (`/areas/...`)
- A page for each category (`/hair/`, `/nails/`, `/beauty/`, `/piercing/`, `/filler/`) and for each treatment inside it, e.g. `/filler/lip-filler/`
- Location-based titles and meta descriptions ("Lip Filler in [TOWN]")
- Canonical URLs, Open Graph tags and breadcrumbs
- Schema.org structured data: BeautySalon, Service, FAQPage and BreadcrumbList
- Aftercare guides, FAQ, prices, about, gallery and contact pages
- `sitemap.xml` and `robots.txt`

## Before launch

- Replace every `[PLACEHOLDER]`. Search for `[` to find them.
- Add real photos in place of the `[Photo]` boxes.
- Add real client reviews only.
- Have the owner check the piercing and filler wording, age policies and aftercare.
