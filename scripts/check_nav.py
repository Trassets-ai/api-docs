"""Prüft docs.json auf Nav-Drift zwischen den Sprachen (Anlass: Dashboard-Edit 2e6dd0d)."""
import json
import os
import sys


def pages(lang: dict) -> set[str]:
    return {p for t in lang["tabs"] for g in t["groups"] for p in g.get("pages", [])}


def key(page: str) -> str:
    # en/index ↔ index, v1/x ↔ de/v1/x: der Sprachumschalter mappt über das Präfix
    return page[3:] if page.startswith(("en/", "de/")) else page


errors = []
for v in json.load(open("docs.json"))["navigation"]["versions"]:
    if v.get("tag") == "Deprecated":
        continue
    langs = {l["language"]: pages(l) for l in v["languages"]}
    en, de = langs["en"], langs["de"]
    for p in sorted(en & de):
        errors.append(f"{v['version']}: {p} steht in EN- und DE-Nav (Mintlify zeigt nur einen Sprachkontext)")
    for p in sorted({key(p) for p in en} ^ {key(p) for p in de}):
        errors.append(f"{v['version']}: {p} fehlt in einer Sprache")
    for p in sorted(en | de):
        if not os.path.exists(p + ".mdx"):
            errors.append(f"{v['version']}: {p}.mdx existiert nicht")

print("\n".join(errors) or "Nav OK")
sys.exit(1 if errors else 0)
