#!/usr/bin/env python3
"""Build a multi-page static site from the curriculum and its session files.

Output layout (default: ./_site):
  index.html                      overview, session map, shopping list
  <stage>/index.html              list of the sessions in one stage
  <stage>/week-NN-session-x.html  one page per session
"""

from __future__ import annotations

import html
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "11_year_old_robotics_python_curriculum.md"
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "_site"
TITLE = "Python and robotics"
STAGES = (
    ("python", "Python basics", "Python", "Write and change short Python programs in the browser."),
    ("pico", "Pico 2 electronics", "Pico 2", "Control LEDs, buttons, dials and a buzzer with a Raspberry Pi Pico 2."),
    ("buggy", "Wheeled buggy", "Buggy", "Optional: build and program a small robot buggy."),
    ("pidog", "PiDog V2", "PiDog", "Build and program the SunFounder PiDog V2 with a Raspberry Pi 5."),
)
SESSION_NAME = re.compile(r"week-(\d+)-session-([ab])\.md$")
MARKDOWN_LINK = re.compile(r"(?<!!)\]\(([^)]+)\)")


def session_key(path: Path) -> str:
    """Progress key prefix. Keep it stable so saved ticks survive layout changes."""
    match = SESSION_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"Unexpected session filename: {path}")
    return f"session-{path.parent.name}-{int(match.group(1)):02d}-{match.group(2)}"


def out_path(source: Path) -> Path:
    """Output file (relative to OUT) for a markdown source file."""
    source = source.resolve()
    if source == INDEX.resolve():
        return Path("index.html")
    return Path(source.parent.name) / source.with_suffix(".html").name


def relative_href(from_page: Path, to_page: Path) -> str:
    return os.path.relpath(to_page, from_page.parent).replace(os.sep, "/")


def rewrite_links(text: str, source: Path, page: Path, known: set[Path]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        file_part, _, fragment = target.partition("#")
        destination = (source.parent / file_part).resolve()
        if destination not in known:
            raise ValueError(f"Unresolved link in {source.name}: {target}")
        href = relative_href(page, out_path(destination))
        return "](" + href + (f"#{fragment}" if fragment else "") + ")"

    return MARKDOWN_LINK.sub(replace, text)


def render(markdown: str) -> str:
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
  --done: #2f8a3b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--background);
  color: var(--ink);
  font: 17px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: #075d73; text-underline-offset: .15em; }
a:hover { color: var(--accent-dark); }
a:focus-visible, button:focus-visible, input:focus-visible { outline: 3px solid #e6a638; outline-offset: 3px; }
.toolbar {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: .7rem max(1rem, calc((100vw - 960px) / 2));
  color: white; background: #153c48; box-shadow: 0 3px 15px #153c4822;
}
.toolbar .brand { color: white; font-weight: 700; text-decoration: none; white-space: nowrap; }
.toolbar nav { display: flex; flex-wrap: wrap; gap: .9rem; }
.toolbar nav a { color: #f8ffff; font-size: .92rem; }
.toolbar nav a[aria-current="page"] { font-weight: 700; text-decoration-thickness: 2px; }
main { max-width: 960px; margin: 0 auto; padding: 1.4rem 1.2rem 4rem; }
h1, h2, h3, h4 { line-height: 1.25; scroll-margin-top: 5rem; }
h1 { font-size: clamp(1.8rem, 4.5vw, 2.6rem); letter-spacing: -.03em; margin-top: .4rem; }
h2 { margin-top: 2.4rem; font-size: 1.5rem; }
h3 { font-size: 1.2rem; }
p, li { max-width: 75ch; }
table {
  display: block; width: max-content; max-width: 100%; overflow-x: auto;
  border-collapse: collapse; background: var(--paper);
  border: 1px solid var(--line); border-radius: .6rem;
}
th, td { min-width: 8rem; padding: .55rem .7rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }
th { background: var(--soft); }
tr:last-child td { border-bottom: none; }
tr:has(td:first-child strong) { background: #eff7f5; }
code { padding: .1em .25em; border-radius: .25em; background: #e9efef; }
pre { overflow-x: auto; padding: 1rem; border-radius: .5rem; background: #e9efef; }
pre code { padding: 0; }
.breadcrumb { margin: 0; color: var(--muted); font-size: .92rem; }
.card {
  margin: 1rem 0; padding: 1.2rem 1.4rem;
  border: 1px solid var(--line); border-left: .4rem solid var(--accent); border-radius: .7rem;
  background: var(--paper); box-shadow: 0 2px 9px #153c4808;
}
.card.is-done { border-left-color: var(--done); background: #f6fbf5; }
.card ul li { margin: .35rem 0; }
input[type="checkbox"] { accent-color: var(--accent); width: 1.15rem; height: 1.15rem; cursor: pointer; vertical-align: -.15em; }
.done-toggle {
  display: inline-flex; align-items: center; gap: .45rem;
  margin: .2rem 0 .4rem; padding: .35rem .8rem;
  border: 1px solid var(--line); border-radius: 999px; background: var(--soft);
  font-weight: 650; cursor: pointer;
}
.card.is-done .done-toggle { background: #d9f0d6; border-color: #9fd19a; }
a.map-done::after { content: " ✓"; color: var(--done); font-weight: 700; }
.stage-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: .8rem; margin: 1rem 0; }
.stage-grid a {
  display: block; padding: 1rem; border: 1px solid var(--line); border-radius: .7rem;
  background: var(--paper); color: var(--ink); text-decoration: none;
}
.stage-grid a:hover { border-color: var(--accent); }
.stage-grid strong { display: block; color: var(--accent-dark); font-size: 1.05rem; }
.stage-grid span { color: var(--muted); font-size: .9rem; }
.stage-progress { display: block; margin-top: .4rem; color: var(--done); font-weight: 650; font-size: .88rem; }
.stage-grid .stage-progress { color: var(--done); }
.pager { display: flex; justify-content: space-between; gap: 1rem; margin-top: 2rem; }
.pager a {
  flex: 1; max-width: 48%; padding: .8rem 1rem; border: 1px solid var(--line); border-radius: .6rem;
  background: var(--paper); text-decoration: none;
}
.pager a small { display: block; color: var(--muted); }
.pager .next { text-align: right; margin-left: auto; }
.progress-box { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; margin: 1rem 0; padding: .9rem 1rem;
  background: var(--paper); border: 1px solid var(--line); border-radius: .7rem; }
.progress-box strong { margin-right: .5rem; }
.progress-box button {
  border: 1px solid #9eb8b8; border-radius: .45rem; padding: .35rem .65rem;
  background: white; color: var(--ink); cursor: pointer; font: inherit; font-size: .9rem;
}
.progress-note { color: var(--muted); font-size: .85rem; }
@media (max-width: 700px) {
  .toolbar { align-items: flex-start; flex-direction: column; gap: .35rem; }
  main { padding: 1rem .8rem 3rem; }
  .card { padding: 1rem; }
  .pager { flex-direction: column; }
  .pager a { max-width: none; }
}
@media print {
  body { background: white; font-size: 11pt; }
  .toolbar, .progress-box, .done-toggle, .pager { display: none !important; }
  main { max-width: none; padding: 0; }
  .card { box-shadow: none; border-color: #bbb; }
  a { color: inherit; }
}
"""


SCRIPT = r"""
(() => {
  // Progress is kept in this browser's localStorage. No server is used.
  const STORE_KEY = "au-kids-learn-coding:progress:v1";
  const SESSION_HREF = /\/(python|pico|buggy|pidog)\/week-(\d+)-session-([ab])\.html$/;
  const note = document.getElementById("progress-note");
  let progress = {};
  let storageOk = true;
  const warn = () => { if (note) note.textContent = "This browser cannot save ticks. Use “Save progress to a file”."; };
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
    if (saved && typeof saved === "object" && !Array.isArray(saved)) progress = saved;
  } catch (error) { storageOk = false; warn(); }
  function save() {
    if (!storageOk) return;
    try { localStorage.setItem(STORE_KEY, JSON.stringify(progress)); } catch (error) { storageOk = false; warn(); }
  }

  const boxes = [];
  const card = document.querySelector(".card[data-session]");
  if (card) {
    const id = card.dataset.session;
    const toggle = document.createElement("label");
    toggle.className = "done-toggle";
    const doneBox = document.createElement("input");
    doneBox.type = "checkbox";
    doneBox.dataset.key = `${id}:done`;
    toggle.append(doneBox, document.createTextNode(" Session done"));
    card.querySelector("h1").after(toggle);
    boxes.push(doneBox);
    card.querySelectorAll('ul input[type="checkbox"]').forEach((box, index) => {
      box.disabled = false;
      box.removeAttribute("disabled");
      box.dataset.key = `${id}:item-${index}`;
      boxes.push(box);
    });
  }

  const sessionLinks = [];
  for (const link of document.querySelectorAll("main a[href]")) {
    const match = new URL(link.href, location.href).pathname.match(SESSION_HREF);
    if (match && !link.closest(".pager")) {
      sessionLinks.push([link, `session-${match[1]}-${match[2].padStart(2, "0")}-${match[3]}`]);
    }
  }

  const doneKeys = () => Object.keys(progress).filter((k) => k.endsWith(":done"));

  function render() {
    for (const box of boxes) box.checked = progress[box.dataset.key] === true;
    if (card) card.classList.toggle("is-done", progress[`${card.dataset.session}:done`] === true);
    for (const [link, id] of sessionLinks) link.classList.toggle("map-done", progress[`${id}:done`] === true);
    for (const el of document.querySelectorAll("[data-stage-progress]")) {
      const done = doneKeys().filter((k) => k.startsWith(`session-${el.dataset.stageProgress}-`)).length;
      el.textContent = done ? `${done} of ${el.dataset.total} done` : "";
    }
    const count = document.getElementById("progress-count");
    if (count) count.textContent = `${doneKeys().length} of ${count.dataset.total} sessions done`;
  }

  for (const box of boxes) {
    box.addEventListener("change", () => {
      if (box.checked) progress[box.dataset.key] = true;
      else delete progress[box.dataset.key];
      save();
      render();
    });
  }

  const exportButton = document.getElementById("progress-export");
  if (exportButton) {
    exportButton.addEventListener("click", () => {
      const blob = new Blob([JSON.stringify({ app: "au-kids-learn-coding", version: 1, progress }, null, 2)],
        { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `coding-progress-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
    });
    const fileInput = document.getElementById("progress-file");
    document.getElementById("progress-import").addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", async () => {
      const file = fileInput.files[0];
      fileInput.value = "";
      if (!file) return;
      try {
        const data = JSON.parse(await file.text());
        if (data.app !== "au-kids-learn-coding" || typeof data.progress !== "object" || Array.isArray(data.progress)) {
          throw new Error("not a progress file");
        }
        const next = {};
        for (const [key, value] of Object.entries(data.progress)) {
          if (value === true && /^session-(python|pico|buggy|pidog)-\d{2}-[ab]:(done|item-\d+)$/.test(key)) next[key] = true;
        }
        progress = next;
        save();
        render();
        note.textContent = `Loaded ${Object.keys(next).length} ticks from ${file.name}.`;
      } catch (error) {
        note.textContent = "That file is not a progress file from this site.";
      }
    });
    document.getElementById("progress-reset").addEventListener("click", () => {
      if (!confirm("Clear all ticks in this browser? Save a file first if you want a copy.")) return;
      progress = {};
      save();
      render();
    });
  }

  render();
})();
"""


def page(page_path: Path, title: str, body: str, current: str = "") -> str:
    def href(target: str) -> str:
        return relative_href(page_path, Path(target))

    links = [("index.html", "Home", "home")] + [(f"{key}/index.html", nav_label, key) for key, _, nav_label, _ in STAGES]
    nav = "\n".join(
        f'      <a href="{href(target)}"' + (' aria-current="page"' if key == current else "") + f">{html.escape(label)}</a>"
        for target, label, key in links
    )
    nav += f'\n      <a href="{href("index.html")}#shopping-list">Shopping list</a>'
    full_title = title if title == TITLE else f"{title} · {TITLE}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{html.escape(full_title)}</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%A4%96%3C/text%3E%3C/svg%3E">
  <link rel="stylesheet" href="{href('style.css')}">
</head>
<body>
  <header class="toolbar">
    <a class="brand" href="{href('index.html')}">{html.escape(TITLE)}</a>
    <nav aria-label="Site">
{nav}
    </nav>
  </header>
  <main>
{body}
  </main>
  <script src="{href('progress.js')}"></script>
</body>
</html>
"""


def session_title(path: Path) -> str:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    if not first.startswith("# "):
        raise ValueError(f"Missing session heading: {path}")
    return first[2:].strip()


def short_title(path: Path) -> str:
    """'Week 1, Session A: Hello world emoji' -> 'Hello world emoji'."""
    return session_title(path).split(":", 1)[-1].strip()


def write(rel: Path, content: str) -> None:
    target = OUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def stage_page_body(key: str, label: str, blurb: str, paths: list[Path]) -> str:
    rows: dict[int, dict[str, Path]] = {}
    for path in paths:
        match = SESSION_NAME.fullmatch(path.name)
        rows.setdefault(int(match.group(1)), {})[match.group(2)] = path
    table = ["<table>", "<thead><tr><th>Week</th><th>Session A</th><th>Session B</th></tr></thead>", "<tbody>"]
    for week in sorted(rows):
        cells = []
        for part in "ab":
            path = rows[week].get(part)
            cells.append(f'<td><a href="{out_path(path).name}">{html.escape(short_title(path))}</a></td>' if path else "<td></td>")
        table.append(f"<tr><td>{week}</td>{''.join(cells)}</tr>")
    table += ["</tbody>", "</table>"]
    note = (
        "<p>If you do both robots, finish the buggy first, then use these PiDog weeks as calendar Weeks 21–30.</p>\n"
        if key == "pidog" else ""
    )
    return (
        f'<p class="breadcrumb"><a href="../index.html">Home</a> › {html.escape(label)}</p>\n'
        f"<h1>{html.escape(label)}</h1>\n<p>{html.escape(blurb)}</p>\n{note}"
        f'<p class="stage-progress" data-stage-progress="{key}" data-total="{len(paths)}"></p>\n'
        + "\n".join(table)
    )


def pager(paths: list[Path], index: int, label: str) -> str:
    parts = ['<nav class="pager" aria-label="Previous and next session">']
    if index > 0:
        prev = paths[index - 1]
        parts.append(f'<a class="prev" href="{out_path(prev).name}"><small>← Previous</small>{html.escape(session_title(prev))}</a>')
    else:
        parts.append(f'<a class="prev" href="index.html"><small>← Back to</small>{html.escape(label)}</a>')
    if index + 1 < len(paths):
        nxt = paths[index + 1]
        parts.append(f'<a class="next" href="{out_path(nxt).name}"><small>Next →</small>{html.escape(session_title(nxt))}</a>')
    else:
        parts.append('<a class="next" href="../index.html#session-map"><small>Next →</small>Choose the next stage</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def main() -> None:
    sessions = {key: sorted((ROOT / "sessions" / key).glob("week-*-session-*.md")) for key, _, _, _ in STAGES}
    all_sessions = [p for key, _, _, _ in STAGES for p in sessions[key]]
    if len(all_sessions) != 60:
        raise ValueError(f"Expected 60 session files, found {len(all_sessions)}")
    known = {p.resolve() for p in all_sessions} | {INDEX.resolve()}

    write(Path("style.css"), STYLE.lstrip())
    write(Path("progress.js"), SCRIPT.lstrip())

    # Home page: overview, stage cards, progress controls.
    home = Path("index.html")
    overview = render(rewrite_links(INDEX.read_text(encoding="utf-8"), INDEX, home, known))
    grid = "\n".join(
        f'<a href="{key}/index.html"><strong>{html.escape(label)}</strong><span>{html.escape(blurb)}</span>'
        f'<span class="stage-progress" data-stage-progress="{key}" data-total="{len(sessions[key])}"></span></a>'
        for key, label, _, blurb in STAGES
    )
    progress_box = f"""
<div class="progress-box" aria-label="Progress">
  <strong id="progress-count" data-total="{len(all_sessions)}"></strong>
  <button type="button" id="progress-export">Save progress to a file</button>
  <button type="button" id="progress-import">Load progress from a file</button>
  <button type="button" id="progress-reset">Clear progress</button>
  <input type="file" id="progress-file" accept="application/json,.json" hidden>
  <span class="progress-note" id="progress-note">Ticks are saved in this browser only.</span>
</div>"""
    heading_end = overview.index("</h1>") + len("</h1>")
    overview = overview[:heading_end] + f'\n<div class="stage-grid">\n{grid}\n</div>' + progress_box + overview[heading_end:]
    write(home, page(home, TITLE, overview, "home"))

    for key, label, _, blurb in STAGES:
        paths = sessions[key]
        stage_page = Path(key) / "index.html"
        write(stage_page, page(stage_page, label, stage_page_body(key, label, blurb, paths), key))
        for index, path in enumerate(paths):
            rel = out_path(path)
            content = render(rewrite_links(path.read_text(encoding="utf-8"), path, rel, known))
            body = (
                f'<p class="breadcrumb"><a href="../index.html">Home</a> › <a href="index.html">{html.escape(label)}</a></p>\n'
                f'<article class="card" data-session="{session_key(path)}">\n{content}</article>\n'
                + pager(paths, index, label)
            )
            write(rel, page(rel, session_title(path), body, key))

    print(f"Wrote {OUT}: home page, {len(STAGES)} stage pages, {len(all_sessions)} session pages")


if __name__ == "__main__":
    main()
