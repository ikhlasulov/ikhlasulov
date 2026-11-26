#!/usr/bin/env python3
"""Give the hero avatar the same static cookie frame as the website.

The generator draws a rotating cookie shape around the avatar plus a
background-coloured copy inside it. Rendered as a still image the rotation
looks misaligned and the pale inner shape hides most of the colour. The
rotating shape also has fewer scallops than the avatar cut-out.

So, in order:
* drop the background-coloured frame that covers the rim;
* rebuild the coloured shape from the avatar cut-out, so the rim and the
  photo share exactly the same scallops, and make it static;
* open it up a little so the rim is ~7 units wide.

Run after the Expressive Profile action has written assets/.
"""
import pathlib
import re

CENTER = 150.0
RIM_SCALE = 210.0 / 196.0


def bounds(d: str):
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d)]
    xs, ys = nums[0::2], nums[1::2]
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def fix(name: str) -> bool:
    p = pathlib.Path(name)
    if not p.exists():
        return False
    text = p.read_text()
    touched = False

    # 1. remove the background-coloured copy that sits on top of the rim
    def drop_pale(match: re.Match) -> str:
        nonlocal touched
        b = bounds(match.group(2))
        has_fill = "fill=" in match.group(1) or "fill=" in match.group(3)
        if b and has_fill and 40 < b[0] < 60 and 192 < b[2] - b[0] < 212:
            touched = True
            return ""
        return match.group(0)

    text = re.sub(r'<path([^>]*)d="([^"]+)"([^>]*)/>', drop_pale, text)

    # 2. rebuild the coloured shape from the avatar cut-out and freeze it
    clip = re.search(r'<clipPath id="ava">\s*<path d="([^"]+)"', text)
    clip_d = clip.group(1) if clip else None

    def make_static(match: re.Match) -> str:
        nonlocal touched
        tag, d = match.group(0), match.group(1)
        b = bounds(d)
        if not (b and max(abs(v) for v in b) < 400):
            return tag
        tag = re.sub(r'\s*class="spin[^"]*"', "", tag, count=1)
        if clip_d:
            tag = re.sub(r'd="[^"]+"', lambda _: f'd="{clip_d}"', tag, count=1)
        transform = (
            f'transform="translate({CENTER} {CENTER}) scale({RIM_SCALE}) '
            f'translate(-{CENTER} -{CENTER})"'
        )
        tag = tag.replace("/>", f" {transform}/>", 1)
        touched = True
        return tag

    text = re.sub(r'<path class="spin[^"]*"[^>]*?d="([^"]+)"[^>]*/>', make_static, text)

    p.write_text(text)
    return touched


changed = False
for svg in ("assets/hero-light.svg", "assets/hero-dark.svg"):
    changed = fix(svg) or changed
print("updated" if changed else "already static")
