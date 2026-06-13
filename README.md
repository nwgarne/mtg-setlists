# mtg-setlists

Per-set card lists for every Magic: the Gathering set, generated from Scryfall's bulk
`default_cards` export (one entry per printing, English where available).

- **Sets:** 1042
- **Card printings:** 115,803
- **Generated:** 2026-06-13
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
