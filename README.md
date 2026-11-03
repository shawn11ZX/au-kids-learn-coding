# Python and robotics for kids

A parent-led plan for an 11-year-old: Python, Raspberry Pi Pico 2 electronics, an optional wheeled buggy, and a SunFounder PiDog V2.

**Read it online:** https://shawn11zx.github.io/au-kids-learn-coding/

## Files

- `11_year_old_robotics_python_curriculum.md`: overview, session map and shopping list.
- `sessions/`: one file per session (Python, Pico, buggy, PiDog).
- `build_html.py`: builds the site into `_site/`: a home page, one page per stage (`python/`, `pico/`, `buggy/`, `pidog/`) and one page per session. Needs `pandoc`.

## Update the site

Edit the markdown, then push to `main`. The GitHub Actions workflow builds the page and publishes it to GitHub Pages.

To preview locally:

```bash
python3 build_html.py
open _site/index.html
```
