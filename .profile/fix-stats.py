#!/usr/bin/env python3
"""Rebuild the language block of the stats cards without web languages.

The generator aggregates languages over all public repositories and has no
per-language filter. For this profile HTML/CSS/JavaScript dominate only
because of the small web tools, so drop them, recompute the shares from the
GitHub API and redraw the bar and the legend in the same geometry.

Run after the Expressive Profile action has written assets/.
"""
import json
import os
import pathlib
import re
import urllib.request

EXCLUDE = {
    # keep the generator's own exclusions
    "Inno Setup", "Batchfile", "PowerShell", "VBScript", "Shell",
    "Makefile", "Dockerfile",
    # web languages that would drown out the desktop projects
    "HTML", "CSS", "JavaScript",
}

API = "https://api.github.com"


def get(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ikhlasulov-profile",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def languages(login: str):
    repos = get(f"{API}/users/{login}/repos?per_page=100&type=owner")
    totals: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        for name, size in get(repo["languages_url"]).items():
            if name in EXCLUDE:
                continue
            totals[name] = totals.get(name, 0) + size
    return sorted(totals.items(), key=lambda item: -item[1])[:7]


def color_map(svg: str):
    found = re.findall(
        r'<circle cx="[^"]+" cy="\d+" r="5" fill="(#[0-9a-fA-F]{6})"/>'
        r'<text[^>]*fill="(#[0-9a-fA-F]{6})"[^>]*>([^<]+)</text>',
        svg,
    )
    colors = {}
    text_fill = "#49454e"
    for color, ink, label in found:
        colors[label.rsplit(" ", 1)[0]] = color
        text_fill = ink
    bar = re.findall(
        r'<rect x="[^"]+" y="334"[^>]*fill="(#[0-9a-fA-F]{6})"/>', svg
    )
    return colors, text_fill, bar


def rebuild(svg: str, label: str, langs, colors, text_fill, palette):
    """Replace the language label, bar and legend at the end of the card."""
    marker = f">{label}</text>"
    position = svg.find(marker)
    if position < 0 or not langs:
        return svg
    end = position + len(marker)
    start = svg.rfind("<text", 0, end)
    close = svg.rfind("</svg>")
    if close < end:
        return svg

    total = sum(size for _, size in langs)
    spare = [color for color in palette if color not in set(colors.values())]
    used = []
    for name, _ in langs:
        color = colors.get(name)
        if not color:
            color = spare.pop(0) if spare else palette[-1]
        used.append(color)

    # bar: 784 units wide, 4 unit gaps, like the generator
    gaps = 4 * (len(langs) - 1)
    raw = [max(8.0, (784 - gaps) * size / total) for _, size in langs]
    factor = (784 - gaps) / sum(raw)
    x = 28.0
    rects = []
    for width, color in zip((value * factor for value in raw), used):
        rects.append(
            f'<rect x="{x:.1f}" y="334" width="{width:.1f}" '
            f'height="14" rx="7" fill="{color}"/>'
        )
        x += width + 4

    # legend: same flow and wrapping as the generator
    x, row = 28.0, 0
    items = []
    for (name, size), color in zip(langs, used):
        share = f"{100 * size / total:.1f}%".replace(".0%", "%")
        text = f"{name} {share}"
        width = 15 + len(text) * 8.4 + 18
        if x + width > 840 - 28:
            x, row = 28.0, row + 1
        items.append((x, row, text, color))
        x += width

    label_markup = svg[start:end]
    body = [
        label_markup,
        '<g class="grow" style="animation-delay:.4s">',
        "".join(rects),
        "</g>",
    ]
    for index, (x, row, text, color) in enumerate(items):
        y = 372 + row * 26
        body.append(
            f'<g class="fade" style="animation-delay:{0.6 + index * 0.06:.2f}s">'
            f'<circle cx="{x + 5:.1f}" cy="{y - 5}" r="5" fill="{color}"/>'
            f'<text x="{x + 15:.1f}" y="{y}.0" fill="{text_fill}" text-anchor="start" '
            f'style="font-size:14px;font-weight:500;">{text}</text></g>'
        )
    result = svg[:start] + "".join(body) + svg[close:]

    height = 400 + row * 26
    if height != 400:
        result = result.replace('height="400" viewBox="0 0 840 400"', f'height="{height}" viewBox="0 0 840 {height}"', 1)
        result = result.replace('width="840" height="400" rx="32"', f'width="840" height="{height}" rx="32"', 1)
    return result


def main():
    profile = json.loads(pathlib.Path("profile.json").read_text())
    label = profile.get("stats", {}).get("languages", "Public project languages")
    langs = languages(profile.get("login") or "ikhlasulov")
    if not langs:
        print("no languages")
        return

    touched = False
    for name in ("assets/stats-light.svg", "assets/stats-dark.svg"):
        path = pathlib.Path(name)
        if not path.exists():
            continue
        text = path.read_text()
        colors, text_fill, palette = color_map(text)
        new = rebuild(text, label, langs, colors, text_fill, palette)
        if new != text:
            path.write_text(new)
            touched = True

    print("updated" if touched else "already filtered")
    print(", ".join(f"{name} {size}" for name, size in langs))


if __name__ == "__main__":
    main()
