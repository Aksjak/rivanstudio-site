#!/usr/bin/env python3
"""Builds the static Rivan Studio site (English at /, Norwegian at /no/) from template.html.

This src/ folder is the single source of truth. Edit template.html (and i18n-no.json for the
Norwegian strings), then build: index.html and no/index.html are generated, so edits made
directly in them are overwritten by the next build.

Everything is plain HTML: no cookies, trackers or third-party requests.
Run: python3 src/build.py   (writes into the repo root)
"""
import json, re, pathlib, html
from urllib.parse import quote

SRC = pathlib.Path(__file__).parent
OUT = SRC.parent
SITE = "https://rivanstudio.com"

tpl = (SRC / "template.html").read_text(encoding="utf-8")
no = json.loads((SRC / "i18n-no.json").read_text(encoding="utf-8"))
head = json.loads((SRC / "head.json").read_text(encoding="utf-8"))
faq = json.loads((SRC / "faq.json").read_text(encoding="utf-8"))


def faq_html(lang):
    items = []
    for q in faq[lang]:
        items.append('<details class="qa"><summary>%s</summary><p>%s</p></details>'
                     % (html.escape(q["q"]), html.escape(q["a"])))
    return "\n".join(items)


def jsonld(lang):
    h = head[lang]
    url = SITE + ("/" if lang == "en" else "/no/")
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": SITE + "/#org",
        "name": "Rivan Studio",
        "url": SITE + "/",
        "logo": SITE + "/favicon.png",
        "email": "partnerships@rivanstudio.com",
        "description": h["description"],
        "address": {"@type": "PostalAddress", "addressCountry": "NO"},
        "identifier": {"@type": "PropertyValue", "propertyID": "Organisasjonsnummer", "value": "937616716"},
        "sameAs": [
            "https://www.instagram.com/elisesayerhome/",
            "https://www.youtube.com/channel/UCK6yLrLOdGmpm2PHdUyKXiw",
            "https://www.tiktok.com/@orinundercontrol",
            "https://www.instagram.com/orinundercontrol/",
            "https://www.instagram.com/adanorlin/",
            "https://www.instagram.com/veralastlight/",
        ],
    }
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": h["service_name"],
        "serviceType": h["service_type"],
        "provider": {"@id": SITE + "/#org"},
        "areaServed": "Europe",
        "url": url,
        "description": h["description"],
        "offers": [
            {"@type": "Offer", "name": h["offer1"], "price": "990", "priceCurrency": "NOK",
             "priceSpecification": {"@type": "PriceSpecification", "price": "990", "priceCurrency": "NOK", "valueAddedTaxIncluded": False}},
            {"@type": "Offer", "name": h["offer2"], "price": "2490", "priceCurrency": "NOK",
             "priceSpecification": {"@type": "PriceSpecification", "price": "2490", "priceCurrency": "NOK", "valueAddedTaxIncluded": False}},
        ],
    }
    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "en" if lang == "en" else "nb",
        "mainEntity": [{"@type": "Question", "name": q["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in faq[lang]],
    }
    video = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": h["video_name"],
        "description": h["video_desc"],
        "thumbnailUrl": SITE + "/media/showreel-orin-poster.jpg",
        "contentUrl": SITE + "/media/showreel-orin.mp4",
        "uploadDate": "2026-09-28",
        "duration": "PT6S",
        "publisher": {"@id": SITE + "/#org"},
    }
    return "\n".join('<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)
                     for o in (org, service, video, faqpage))


def mail_query(lang, ch):
    """Query string for an order mailto: subject plus a short body template, with the character filled in."""
    h = head[lang]
    subject = h["mail_subject"] + (": " + ch if ch else "")
    body = h["mail_body"].replace("{ch}", ch or h["mail_any"])
    return "subject=" + quote(subject) + "&amp;body=" + quote(body)


def translate(page):
    def rep(m):
        key = m.group(4)
        if key not in no:
            return m.group(0)
        val = no[key] if m.group(3) else html.escape(no[key], quote=False)
        return m.group(1) + val + m.group(6)
    pat = re.compile(r'(<(\w+)\b[^>]*\bdata-i18n(-html)?="([\w-]+)"[^>]*>)(.*?)(</\2>)', re.S)
    return pat.sub(rep, page)


for lang in ("en", "no"):
    h = head[lang]
    url = SITE + ("/" if lang == "en" else "/no/")
    page = tpl
    subs = {
        "{{lang}}": "en" if lang == "en" else "nb",
        "{{title}}": html.escape(h["title"]),
        "{{description}}": html.escape(h["description"]),
        "{{og_title}}": html.escape(h["og_title"]),
        "{{og_desc}}": html.escape(h["og_desc"]),
        "{{og_locale}}": "en_GB" if lang == "en" else "nb_NO",
        "{{url}}": url,
        "{{en_pressed}}": "true" if lang == "en" else "false",
        "{{no_pressed}}": "true" if lang == "no" else "false",
        "{{faq}}": faq_html(lang),
        "{{jsonld}}": jsonld(lang),
    }
    for k, v in subs.items():
        page = page.replace(k, v)
    page = re.sub(r"\{\{mail:(\w*)\}\}", lambda m: mail_query(lang, m.group(1)), page)
    if lang == "no":
        page = translate(page)
    dest = OUT / ("index.html" if lang == "en" else "no/index.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print("wrote", dest)


# Legal pages for the publishing tool (/privacy/ and /terms/), text from legal.json, same look as the main page.
LEGAL_CSS = ('@font-face{font-family:"Instrument Serif";src:url("/fonts/InstrumentSerif-normal-400.woff2") format("woff2");font-display:swap}'
             ':root{--paper:#f5f4f0;--ink:#161618;--ink-3:#74727a;--accent:#2e5a46}'
             '@media (prefers-color-scheme:dark){:root{--paper:#141416;--ink:#ecebe7;--ink-3:#a19fa8;--accent:#8fc2a8}}'
             'body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:17px;line-height:1.6}'
             'main{max-width:680px;margin:0 auto;padding:40px 16px 64px}'
             'h1{font-family:"Instrument Serif",Georgia,serif;font-weight:400;font-size:clamp(30px,6vw,44px);line-height:1.1;margin:28px 0 6px}'
             '.upd{color:var(--ink-3);margin:0 0 28px}a{color:var(--accent);overflow-wrap:anywhere}.home{text-decoration:none;font-family:"Instrument Serif",Georgia,serif;font-size:22px;color:var(--ink)}')
legal = json.loads((SRC / "legal.json").read_text(encoding="utf-8"))


def linkify(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"(https://[^\s)]+?)(?=[.)]*(\s|$))", r'<a href="\1" rel="noopener">\1</a>', t)
    t = re.sub(r"(?<![/\w])(myaccount\.google\.com/permissions)", r'<a href="https://\1" rel="noopener">\1</a>', t)
    return re.sub(r"([\w.]+@rivanstudio\.com)", r'<a href="mailto:\1">\1</a>', t)


for slug, d in legal.items():
    body = "\n".join("<p>%s</p>" % linkify(p) for p in d["paras"])
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><link rel="canonical" href="%s/%s/"><link rel="icon" href="/favicon.png" type="image/png">'
            '<style>%s</style></head><body><main><a class="home" href="/">Rivan Studio</a>'
            '<h1>%s</h1><p class="upd">%s</p>\n%s\n</main></body></html>\n'
            % (html.escape(d["title"]), SITE, slug, LEGAL_CSS, html.escape(d["title"]), html.escape(d["updated"]), body))
    dest = OUT / slug / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print("wrote", dest)
