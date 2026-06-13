#!/usr/bin/env python3
"""Generate a per-set card-list markdown file for every MTG set from the Scryfall
default_cards bulk export (streamed line-by-line, constant memory). Writes into the
mtg-setlists repo: README.md, SETS.md (index), and sets/<code>.md per set."""
import json, re, os, shutil
from collections import defaultdict

WORK = os.environ.get("SETLIST_WORK", ".")
REPO = os.environ.get("SETLIST_REPO", ".")
GEN_DATE = os.environ.get("SETLIST_DATE", "")

# --- set metadata ---
sets_meta = {s["code"]: s for s in json.load(open(f"{WORK}/sets-raw.json"))["data"]}

# --- stream the bulk export, grouping slim card records by set ---
by_set = defaultdict(list)
seen_lines = 0
with open(f"{WORK}/default-cards.json") as f:
    for line in f:
        line = line.strip()
        if not line or line in ("[", "]"):
            continue
        if line.endswith(","):
            line = line[:-1]
        try:
            c = json.loads(line)
        except json.JSONDecodeError:
            continue
        seen_lines += 1
        by_set[c["set"]].append({
            "cn": c.get("collector_number", "") or "",
            "name": c.get("name", "") or "",
            "rarity": c.get("rarity", "") or "",
            "mana": c.get("mana_cost", "") or "",
            "type": c.get("type_line", "") or "",
            "uri": (c.get("scryfall_uri") or "").split("?")[0],
        })

def cn_key(cn):
    # natural sort: zero-pad digit runs so plain string sort orders numerically
    return re.sub(r"\d+", lambda m: m.group().zfill(8), cn)

def esc(s):
    return (s or "").replace("|", "\\|").replace("—", "-").replace("–", "-").replace("\n", " ").strip()

def safe_code(code):
    return re.sub(r"[^a-z0-9_.-]", "_", code.lower())

if os.path.isdir(f"{REPO}/sets"):
    shutil.rmtree(f"{REPO}/sets")  # rebuild the whole tree so stale flat files / years clear
os.makedirs(f"{REPO}/sets", exist_ok=True)

index = []
total_cards = 0
for code in sorted(set(sets_meta) | set(by_set)):
    cards = by_set.get(code, [])
    meta = sets_meta.get(code, {})
    name = meta.get("name", code.upper())
    stype = meta.get("set_type", "")
    released = meta.get("released_at", "")
    cards.sort(key=lambda c: cn_key(c["cn"]))
    n = len(cards)
    total_cards += n
    out = []
    out.append(f"# {name} ({code.upper()})\n")
    out.append(f"- **Set code:** {code}")
    if stype:
        out.append(f"- **Type:** {stype}")
    out.append(f"- **Cards:** {n}")
    if released:
        out.append(f"- **Released:** {released}")
    out.append(f"- **Scryfall:** <https://scryfall.com/sets/{code}>\n")
    if n:
        out.append("| # | Card | Rarity | Mana | Type |")
        out.append("|---|------|--------|------|------|")
        for c in cards:
            link = f"[{esc(c['name'])}]({c['uri']})" if c["uri"] else esc(c["name"])
            out.append(f"| {esc(c['cn'])} | {link} | {esc(c['rarity'])} | {esc(c['mana'])} | {esc(c['type'])} |")
    else:
        out.append("_No cards in the Scryfall bulk export yet (upcoming or unreleased set)._")
    year = (released or "")[:4] or "undated"
    ydir = f"{REPO}/sets/{year}"
    os.makedirs(ydir, exist_ok=True)
    open(f"{ydir}/{safe_code(code)}.md", "w").write("\n".join(out) + "\n")
    index.append({"code": code, "name": name, "type": stype, "n": n, "released": released, "year": year})

# --- SETS.md index (newest first) ---
index.sort(key=lambda r: (r["released"] or "0000-00-00", r["code"]), reverse=True)
idx = []
idx.append(f"# All sets ({len(index)})\n")
idx.append("Every Magic: the Gathering set with cards in the Scryfall bulk export, newest first. The Cards column is the printings present in the set (including alternate treatments).\n")
idx.append("| Released | Code | Set | Type | Cards |")
idx.append("|----------|------|-----|------|------:|")
for r in index:
    idx.append(f"| {r['released'] or '-'} | `{r['code']}` | [{esc(r['name'])}](sets/{r['year']}/{safe_code(r['code'])}.md) | {r['type'] or '-'} | {r['n']} |")
open(f"{REPO}/SETS.md", "w").write("\n".join(idx) + "\n")

# --- README ---
cards_disp = f"{total_cards:,}".replace(",", "%2C")
readme = f"""# mtg-setlists

![Sets](https://img.shields.io/badge/sets-{len(index)}-blue) ![Card printings](https://img.shields.io/badge/card%20printings-{cards_disp}-brightgreen)

Per-set card lists for every Magic: the Gathering set, generated from Scryfall's bulk
`default_cards` export (one entry per printing, English where available).

- **Sets:** {len(index)}
- **Card printings:** {total_cards:,}
- **Generated:** {GEN_DATE}
- **Source:** Scryfall bulk data, <https://scryfall.com/docs/api/bulk-data>

## Layout

- `sets/<year>/<code>.md` one file per set, grouped into folders by release year, with
  cards in collector-number order with rarity, mana cost, and type. Example:
  `sets/2026/msh.md` for Marvel Super Heroes.
- `SETS.md` an index of every set (code, name, type, card count, release date) linking
  to each file.

## Notes

- Card counts are the printings present in the bulk export and include alternate-art,
  borderless, extended-art, promo, and other special treatments, so they match the
  Scryfall set page total rather than the smaller "main set" count.
- Type lines use a hyphen separator in place of the printed em dash.
- Card and set data are from Scryfall; see Scryfall's data terms for reuse.

Regenerate by re-running the generator against a fresh Scryfall bulk export.
"""
open(f"{REPO}/README.md", "w").write(readme)

print(f"streamed {seen_lines} card lines")
print(f"sets written: {len(index)} | total cards: {total_cards}")
print(f"MSH cards: {len(by_set.get('msh', []))}")
print(f"sample big sets:", {c: len(by_set[c]) for c in ('neo','mh3','blb','fdn') if c in by_set})
