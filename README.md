# Onesimus & Taonanyasha — Wedding Vision Board
### Wednesday 7th April 2027 · Siyekhya Estate

A self-contained build system for the wedding vision board.
Edit text in `board-config.json`, swap images in `images/`, run `build.py` to regenerate.

---

## Project structure

```
wedding-board/
├── board-config.json      ← ALL text content lives here
├── build.py               ← Generates output/index.html
├── images/                ← All 20 board images (named by section)
│   ├── 01-welcome-sign.jpeg
│   ├── 02-welcome-story.jpeg
│   ├── 03-ceremony-arch.jpeg
│   ├── 04-ceremony-aisle.jpeg
│   ├── 05-ceremony-seating.jpeg
│   ├── 06-ceremony-smoke.jpeg
│   ├── 07-cocktail-cabana.jpeg
│   ├── 07-cocktail-terrace.jpeg
│   ├── 08-cocktail-bar.jpeg
│   ├── 09-looks-ceremony.jpeg
│   ├── 10-looks-reception.jpeg
│   ├── 11-entryway-corridor.jpeg
│   ├── 12-entryway-seating.jpeg
│   ├── 13-reception-couch.jpeg
│   ├── 14-reception-monogram.jpeg
│   ├── 15-tables-layout.jpeg
│   ├── 16-cake-design.jpeg
│   ├── 17-cake-stand.jpeg
│   ├── 18-tables-setting.jpeg
│   └── 19-tables-runner.jpeg
└── output/
    └── index.html         ← The generated board (open in browser)
```

---

## How to update

### Update any text description
1. Open `board-config.json`
2. Find the section (e.g. `"arrival"`, `"ceremony"`, `"reception"`)
3. Edit the `"brief"`, `"notes"`, or any text field
4. Run `python3 build.py`

**Example — change the arrival brief:**
```json
"arrival": {
  "brief": "Your new text here...",
  ...
}
```

### Update an image
1. Save your new image into the `images/` folder
2. Update the `"file"` path in `board-config.json` for that image
3. Run `python3 build.py`

**Example — update the ceremony arch photo:**
```json
"arch": {
  "key": "arch",
  "file": "images/new-arch-photo.jpeg",   ← change this
  "caption": "Arch, aisle & seating",
  "alt": "Ceremony arch and aisle"
}
```

### Build the board
```bash
cd wedding-board
python3 build.py
```

Output: `output/index.html` — open in any browser, or deploy to GitHub Pages.

### Validate (check all images exist before building)
```bash
python3 build.py --validate
```

---

## Deploy to GitHub Pages (claudetj.github.io)

1. Build the board: `python3 build.py`
2. Push `output/index.html` to your GitHub repo as `index.html`
3. Enable GitHub Pages on the repo (Settings → Pages → main branch)
4. Share the link

---

## Section map (board-config.json keys)

The board is split into three environments, driven by `day_overview.phases`.
Each phase has an `id` (its anchor) and a `sections` list naming the board
sections that live inside it — reorder or move a key to move a section.

| Environment        | Key            | Section on board         | Images |
|--------------------|----------------|--------------------------|--------|
| I · Ceremony       | `arrival`      | Arrival & Welcome        | 01, 02 |
|                    | `ceremony`     | The Setting              | 03–06  |
| II · Cocktail Hour | `cocktail`     | Lounge & Bar             | 07, 08 |
| III · Reception    | `entryway`     | The Entryway             | 11, 12 |
|                    | `reception`    | The Room (+ `tables`)    | 13–15, 18, 19 |
|                    | `cake`         | The Cake                 | 16, 17 |

`looks` (09, 10) is kept in the config but not rendered.

---

## For Claude Code

To update text: `edit board-config.json → run python3 build.py`
To update image: `replace file in images/ → update file path in config → run python3 build.py`
To add a section: add a section builder function in `build.py` + add section data to config
