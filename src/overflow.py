"""Lists elements that stick out past the viewport (horizontal overflow) at phone and desktop width."""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for w in (390, 1440):
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(url, wait_until="networkidle")
        print(w, pg.evaluate("""() => {
          const iw = innerWidth, out = [];
          for (const e of document.querySelectorAll('body *')) {
            const r = e.getBoundingClientRect();
            if (r.right > iw + 1 || r.left < -1) out.push(e.tagName.toLowerCase() + '.' + (e.className || '') + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
          }
          return {sw: document.documentElement.scrollWidth, out: out.slice(0, 12)};
        }"""))
    b.close()
