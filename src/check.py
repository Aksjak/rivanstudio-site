#!/usr/bin/env python3
"""Checks the built pages: language, title, JSON-LD validity, leftover placeholders, untranslated strings."""
import re, json, pathlib
root = pathlib.Path(__file__).parent.parent
pat = re.compile(r'data-i18n(?:-html)?="([\w-]+)"[^>]*>(.*?)</', re.S)
pages = {}
for f in ["index.html", "no/index.html"]:
    s = (root / f).read_text(encoding="utf-8")
    pages[f] = s
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    types = [json.loads(x)["@type"] for x in lds]
    print(f, "lang=" + re.search(r'<html lang="(\w+)"', s).group(1),
          "| title=" + re.search(r"<title>(.*?)</title>", s).group(1),
          "| jsonld=", types, "| leftover {{:", "{{" in s)
e = dict(pat.findall(pages["index.html"]))
n = dict(pat.findall(pages["no/index.html"]))
print("untranslated:", [k for k in e if k in n and e[k] == n[k]])
