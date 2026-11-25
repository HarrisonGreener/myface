# My Face

A MySpace-style site for a hair, beauty, nails, piercing and filler studio.

## Editing

Every page is generated from `build.py`.

1. Fill in `CONFIG` at the top of `build.py`: the domain, name, town, address, phone, booking link and hours.
2. Edit treatments, FAQs and aftercare in `CATEGORIES`, `AFTERCARE` and `GENERAL_FAQS`.
3. Run `python3 build.py` to rebuild all the pages, `sitemap.xml` and `robots.txt`.

Styles live in `assets/style.css`.

## What's built for SEO

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
