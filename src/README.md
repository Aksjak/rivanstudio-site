# rivanstudio.com source

`index.html` and `no/index.html` in the repo root are generated. Edit the files here instead:

- `template.html`: the page (English text, CSS, layout). Norwegian text is swapped in by `data-i18n` keys.
- `i18n-no.json`: Norwegian strings for every `data-i18n` / `data-i18n-html` key.
- `head.json`: title, meta and structured-data text per language, plus the order-mail template.
- `faq.json`: FAQ questions and answers per language.

Build and check: `python3 src/build.py && python3 src/check.py` (from the repo root).
Publish (owner's PC): `.\src\publish.ps1 "message"` pulls, builds, checks, commits, pushes and pings IndexNow.

Rules: no cookies, trackers or third-party requests; every video carries the burned-in "AI-generated | fictional character" label; only QA-passed, owner-approved media.
