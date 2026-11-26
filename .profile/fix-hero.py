#!/usr/bin/env python3
"""Keep the hero avatar frame static.

The generator draws a rotating cookie shape around the avatar in the hero
card. Rendered as a still image it looks misaligned with the avatar cut-out,
so drop that one decoration and keep the static frame. The decorative shapes
in the card corners are preserved.

Run after the Expressive Profile action has written assets/.
"""
import pathlib
import re

AVATAR_AREA = 400  # anything inside this box belongs to the avatar block


def avatar_area(path_data: str) -> bool:
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", path_data)]
    xs, ys = nums[0::2], nums[1::2]
    return bool(xs) and max(abs(x) for x in xs) < AVATAR_AREA and max(abs(y) for y in ys) < AVATAR_AREA


def fix(name: str) -> bool:
    p = pathlib.Path(name)
    if not p.exists():
        return False
    text = p.read_text()

    def replace(match: re.Match) -> str:
        return "" if avatar_area(match.group(1)) else match.group(0)

    new = re.sub(r'<path class="spin[^"]*"[^>]*?d="([^"]+)"[^>]*/>', replace, text)
    if new == text:
        return False
    p.write_text(new)
    return True


changed = False
for svg in ("assets/hero-light.svg", "assets/hero-dark.svg"):
    changed = fix(svg) or changed
print("updated" if changed else "already static")
