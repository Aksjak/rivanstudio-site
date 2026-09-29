"""Full-page screenshots of the site at desktop and phone size, using the installed Edge.

Pages are saved as JPG segments (<prefix>-<view>-<lang>-<n>.jpg), because one very tall
screenshot at phone resolution goes past the browser's texture limit and repeats itself.

Usage: python shots.py <base-url> <out-prefix> [en|no|both]
  e.g. python shots.py https://rivanstudio.com ../rivanstudio-site-qa/before
"""
import sys
from playwright.sync_api import sync_playwright

base, prefix = sys.argv[1].rstrip("/"), sys.argv[2]
langs = {"en": "/", "no": "/no/"}
if len(sys.argv) > 3 and sys.argv[3] != "both":
    langs = {sys.argv[3]: langs[sys.argv[3]]}
views = {"desktop": (dict(viewport={"width": 1440, "height": 900}, device_scale_factor=1), 6000),
         "phone": (dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True), 3000)}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    for name, (opts, seg) in views.items():
        ctx = browser.new_context(reduced_motion="reduce", **opts)
        page = ctx.new_page()
        for lang, path in langs.items():
            page.goto(base + path, wait_until="networkidle")
            page.evaluate("document.querySelectorAll('.reveal').forEach(e => e.classList.add('in'))")
            page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
            page.evaluate("async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); }")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(800)
            width, height = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
            n = 0
            for y in range(0, height, seg):
                out = f"{prefix}-{name}-{lang}-{n}.jpg"
                page.screenshot(path=out, full_page=True, type="jpeg", quality=82,
                                clip={"x": 0, "y": y, "width": width, "height": min(seg, height - y)})
                n += 1
            print(name, lang, f"{width}x{height}", n, "segments")
        ctx.close()
    browser.close()
