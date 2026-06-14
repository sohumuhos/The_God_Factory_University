# UI Themes — Classic & "Frosted Obsidian" Glass

**Added:** 2026-06-13. A second interface theme — a dark, Apple-inspired
*liquid-glass* look — selectable at runtime alongside the original terminal theme.

## Using it

Settings → **General → Interface theme**:
- **Classic — Dark Terminal** (default): the original sharp, neon, solid-panel look.
- **Frosted Obsidian — Liquid Glass**: translucent, blurred, rounded panels over an
  animated cyan/gold/violet/green mesh, keeping the dark-academic palette.

The choice is stored in the `ui_theme` setting and applies to **every page** — no
per-page changes are needed.

## Architecture

| File | Role |
|------|------|
| `ui/themes.py` | **Streamlit-free** CSS source. Holds `CLASSIC_CSS`, loads `GLASS_BG_CSS`/`GLASS_GLOBAL_CSS` from the sidecar `.css` files, the `HELPER_TOKENS` per theme, and `build_theme_css(theme)` / `helper_tokens(theme)` / `glass_available()`. No Streamlit import → screenshot-testable. |
| `ui/glass_global.css` | The glass widget stylesheet (~1000 lines, all Streamlit 1.44 widgets). |
| `ui/glass_bg.css` | The animated gradient-mesh background layer (GPU-only `transform` drift). |
| `ui/theme.py` | `active_theme()` reads the setting; `inject_theme()` injects `build_theme_css(active_theme())` once per page; `_panel_attrs()` makes the 5 custom panels (`stat_card`, `level_badge`, `achievement_card`, `completion_burst`, `degree_display`) theme-aware. |
| `.streamlit/config.toml` | `base = "dark"` so `<canvas>`/base-palette widgets (notably `st.dataframe`/glide-data-grid, date pickers) render dark under **both** themes instead of as light blocks. |

`inject_theme()` injects ONE `<style>` block: classic, or `[font @import + glass_bg + glass_global]`.
A bad/unknown `ui_theme`, or missing glass `.css` files, falls back to classic — and
`glass_available()` is the single source of truth so the panel helpers never render glass
while the page injects the classic sheet.

## Design & review process

The glass CSS was produced by a multi-agent workflow (selector inventory → 3 stylistic
variants → judge panel → synthesis) and then **iterated against headless-Chromium
screenshots** of a faithful Streamlit-DOM mock (Playwright). An adversarial review workflow
(selectors / regression / security / perf+a11y) then surfaced defects that were fixed:

- **Font `@import`** moved ahead of all style rules (a `@import` after any rule is dropped).
- **`st.dataframe`** can't be recolored by CSS (it paints to `<canvas>`) → fixed via
  `config.toml base="dark"`, not selectors.
- **Coherent fallback**: helpers + injected sheet agree via `glass_available()`.
- **WCAG AA**: captions/placeholders/locked-achievement text lifted off the failing
  `#606080`/`#404060` tones to `#8a8aae` (≥4.5:1).
- **`prefers-reduced-transparency`** now also drops blur on the inline `.gf-glass` panels,
  the header, code blocks, dropzones, media, tooltips, and dropdowns;
  `prefers-reduced-motion` freezes the mesh and button sheen.
- **Stored-XSS**: user-pasted course titles (and the panel-helper text args) are now
  `html.escape`d before entering `unsafe_allow_html` sinks.
- **GPU**: `backdrop-filter` is confined to bounded/transient surfaces; dropped from the
  high-count code blocks; mesh drifts via `transform` only (no animated `background-position`).

## Known platform limits

- `st.dataframe`'s interior cells are theme-driven (via `config.toml`), **not** CSS — the
  frosted frame is CSS, the grid body inherits the dark base palette.
- `st.toggle`'s baseweb knob has no stable testid; the track themes reliably, the thumb is
  best-effort. Verify in a live 1.44 instance if it matters.

## Dev: screenshotting a theme

The headless harness lives outside the repo (it needs Playwright/Chromium). It imports
`ui.themes.build_theme_css` (no Streamlit needed) and renders a mock page DOM with the same
`data-testid` hooks Streamlit emits, so the glass look can be iterated without running the app.
