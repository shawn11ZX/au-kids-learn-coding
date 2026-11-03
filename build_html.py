#!/usr/bin/env python3
"""Build one offline HTML guide from the curriculum and its session files."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "11_year_old_robotics_python_curriculum.md"
OUTPUT = ROOT / "11_year_old_robotics_python_curriculum.html"
ROUTES = (
    ("python", "Python basics"),
    ("pico", "Pico 2 electronics"),
    ("buggy", "Wheeled buggy"),
    ("pidog", "PiDog V2"),
)
SESSION_NAME = re.compile(r"week-(\d+)-session-([ab])\.md$")
MARKDOWN_LINK = re.compile(r"(?<!!)\]\(([^)]+)\)")


def session_id(path: Path) -> str:
    match = SESSION_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"Unexpected session filename: {path}")
    return f"session-{path.parent.name}-{int(match.group(1)):02d}-{match.group(2)}"


def rewrite_local_links(text: str, source: Path, anchors: dict[Path, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        file_part, _, fragment = target.partition("#")
        destination = (source.parent / file_part).resolve()
        if destination == INDEX.resolve():
            anchor = fragment or "top"
        elif destination in anchors:
            anchor = anchors[destination]
        else:
            raise ValueError(f"Unresolved link in {source.name}: {target}")
        return f"](" + f"#{anchor}" + ")"

    return MARKDOWN_LINK.sub(replace, text)


def session_markdown(path: Path, anchor: str, anchors: dict[Path, str]) -> str:
    text = rewrite_local_links(path.read_text(encoding="utf-8"), path, anchors)
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Missing session heading: {path}")
    lines[0] = "### " + lines[0][2:]
    for number, line in enumerate(lines[1:], start=1):
        if line.startswith("## "):
            lines[number] = "#### " + line[3:]
    return "\n".join(
        (
            f'::: {{#{anchor} .session-card data-route="{path.parent.name}"}}',
            *lines,
            "",
            "[Back to session map](#session-map)",
            ":::",
        )
    )


def build_markdown() -> tuple[str, int]:
    paths: dict[str, list[Path]] = {
        route: sorted((ROOT / "sessions" / route).glob("week-*-session-*.md"))
        for route, _ in ROUTES
    }
    all_sessions = [path for route, _ in ROUTES for path in paths[route]]
    if len(all_sessions) != 60:
        raise ValueError(f"Expected 60 session files, found {len(all_sessions)}")
    anchors = {path.resolve(): session_id(path) for path in all_sessions}

    parts = [
        rewrite_local_links(INDEX.read_text(encoding="utf-8"), INDEX, anchors),
        "# Session guides {#session-guides}",
        "Use the session map above to jump to a lesson. The filter and search controls "
        "below help you find sessions; the complete guide remains available for printing.",
    ]
    for route, label in ROUTES:
        parts.append(f"## {label} {{#{route}-sessions}}")
        parts.extend(session_markdown(path, anchors[path.resolve()], anchors) for path in paths[route])
    return "\n\n".join(parts) + "\n", len(all_sessions)


def render_html(markdown: str) -> str:
    result = subprocess.run(
        [
            "pandoc",
            "--from=markdown+fenced_divs+pipe_tables+task_lists+auto_identifiers",
            "--to=html5",
            "--wrap=none",
        ],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


STYLE = """
:root {
  color-scheme: light;
  --ink: #172b38;
  --muted: #526675;
  --accent: #176c69;
  --accent-dark: #0e504e;
  --line: #d8e4e4;
  --paper: #fff;
  --background: #f3f7f6;
  --soft: #e7f4f1;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--background);
  color: var(--ink);
  font: 16px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: #075d73; text-underline-offset: .15em; }
a:hover { color: var(--accent-dark); }
a:focus-visible, button:focus-visible, input:focus-visible {
  outline: 3px solid #e6a638;
  outline-offset: 3px;
}
.toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: .75rem max(1rem, calc((100vw - 1100px) / 2));
  color: white;
  background: #153c48;
  box-shadow: 0 3px 15px #153c4822;
}
.toolbar strong { font-size: .95rem; white-space: nowrap; }
.toolbar nav { display: flex; flex-wrap: wrap; gap: .75rem; }
.toolbar a { color: #f8ffff; font-size: .9rem; }
main { max-width: 1100px; margin: 0 auto; padding: 1.5rem 1.2rem 5rem; }
h1, h2, h3, h4 { line-height: 1.25; scroll-margin-top: 5rem; }
h1 { font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.035em; }
h2 { margin-top: 3rem; font-size: 1.65rem; }
h3 { margin-top: 0; font-size: 1.28rem; }
h4 { margin-bottom: .6rem; font-size: 1.06rem; color: var(--accent-dark); }
p, li { max-width: 80ch; }
table {
  display: block;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: .6rem;
}
th, td { min-width: 8rem; padding: .55rem .7rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }
th { position: sticky; top: 0; background: var(--soft); }
tr:last-child td { border-bottom: none; }
tr:has(td:first-child strong) { background: #eff7f5; }
code { padding: .1em .25em; border-radius: .25em; background: #e9efef; }
pre { overflow-x: auto; padding: 1rem; border-radius: .5rem; background: #e9efef; }
pre code { padding: 0; }
.session-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .75rem;
  margin: 1.5rem 0;
  padding: 1rem;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: .75rem;
}
.session-controls label { font-weight: 650; }
.session-controls input {
  width: min(100%, 22rem);
  padding: .55rem .7rem;
  border: 1px solid #9eb8b8;
  border-radius: .45rem;
  font: inherit;
}
.route-buttons { display: flex; flex-wrap: wrap; gap: .4rem; }
.route-buttons button {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: .4rem .7rem;
  background: white;
  color: var(--ink);
  cursor: pointer;
  font: inherit;
  font-size: .9rem;
}
.route-buttons button[aria-pressed="true"] { background: var(--accent); color: white; border-color: var(--accent); }
#session-count { color: var(--muted); font-size: .9rem; }
.session-card {
  scroll-margin-top: 5rem;
  margin: 1rem 0 1.5rem;
  padding: 1.2rem 1.4rem;
  border: 1px solid var(--line);
  border-left: .4rem solid var(--accent);
  border-radius: .7rem;
  background: var(--paper);
  box-shadow: 0 2px 9px #153c4808;
}
.session-card:target { outline: 3px solid #dfb34e; outline-offset: 3px; }
.session-card[hidden] { display: none; }
.session-card ul li { margin: .35rem 0; }
.session-card input[type="checkbox"] { accent-color: var(--accent); }
@media (max-width: 700px) {
  .toolbar { align-items: flex-start; flex-direction: column; gap: .35rem; }
  main { padding: 1rem .8rem 3rem; }
  .session-card { padding: 1rem; }
}
@media print {
  body { background: white; font-size: 11pt; }
  .toolbar, .session-controls { display: none !important; }
  main { max-width: none; padding: 0; }
  .session-card, .session-card[hidden] {
    display: block !important;
    break-inside: avoid;
    box-shadow: none;
    border-color: #bbb;
  }
  a { color: inherit; }
  h1, h2, h3, h4 { break-after: avoid; }
}
"""


SCRIPT = """
(() => {
  const search = document.getElementById("session-search");
  const buttons = [...document.querySelectorAll(".route-buttons button")];
  const cards = [...document.querySelectorAll(".session-card")];
  const count = document.getElementById("session-count");
  let route = "all";

  function applyFilters() {
    const query = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    for (const card of cards) {
      const routeMatches = route === "all" || card.dataset.route === route;
      const textMatches = !query || card.textContent.toLocaleLowerCase().includes(query);
      card.hidden = !(routeMatches && textMatches);
      if (!card.hidden) shown++;
    }
    count.textContent = `${shown} of ${cards.length} sessions shown`;
  }

  function selectRoute(next) {
    route = next;
    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.route === route));
    }
    applyFilters();
  }

  for (const button of buttons) {
    button.addEventListener("click", () => selectRoute(button.dataset.route));
  }
  search.addEventListener("input", applyFilters);

  function revealHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = document.getElementById(id);
    if (target && target.classList.contains("session-card") && target.hidden) {
      search.value = "";
      selectRoute("all");
      requestAnimationFrame(() => target.scrollIntoView());
    }
  }
  window.addEventListener("hashchange", revealHash);
  revealHash();
  applyFilters();
})();
"""


def page(body: str, session_count: int) -> str:
    controls = """
<div class="session-controls" role="search" aria-label="Find a session">
  <label for="session-search">Find a session</label>
  <input id="session-search" type="search" placeholder="Try “servo”, “LED”, or “order”">
  <div class="route-buttons" aria-label="Filter by stage">
    <button type="button" data-route="all" aria-pressed="true">All</button>
    <button type="button" data-route="python" aria-pressed="false">Python</button>
    <button type="button" data-route="pico" aria-pressed="false">Pico 2</button>
    <button type="button" data-route="buggy" aria-pressed="false">Buggy</button>
    <button type="button" data-route="pidog" aria-pressed="false">PiDog</button>
  </div>
  <span id="session-count"></span>
</div>"""
    marker = '<section id="session-guides"'
    if marker in body:
        # Pandoc wraps a heading with its section only when --section-divs is used.
        raise ValueError("Unexpected Pandoc section wrapper")
    heading = '<h1 id="session-guides">Session guides</h1>'
    if heading not in body:
        raise ValueError("Session guide heading was not rendered")
    body = body.replace(heading, heading + controls, 1)
    title = "Python and robotics — parent-led curriculum"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{html.escape(title)}</title>
  <style>{STYLE}</style>
</head>
<body id="top">
  <header class="toolbar">
    <strong>Python &amp; robotics · {session_count} sessions</strong>
    <nav aria-label="Page">
      <a href="#top">Overview</a>
      <a href="#session-map">Session map</a>
      <a href="#shopping-list">Shopping list</a>
      <a href="#session-guides">Session guides</a>
    </nav>
  </header>
  <main>
{body}
  </main>
  <script>{SCRIPT}</script>
</body>
</html>
"""


def main() -> None:
    markdown, count = build_markdown()
    body = render_html(markdown)
    output = page(body, count)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({count} sessions)")


if __name__ == "__main__":
    main()
