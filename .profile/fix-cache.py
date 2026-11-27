#!/usr/bin/env python3
"""Give every generated card a content-addressed file name.

GitHub caches README images by URL, so a card rewritten in place can keep
showing the old picture after the action has regenerated it. Appending a
short hash of the file contents makes every version a distinct URL, so a
changed card is fetched immediately while an unchanged one keeps its name.

Run last, after the generator and the other polish steps have written
assets/ and README.md.
"""
import hashlib
import pathlib
import re

ASSETS = pathlib.Path("assets")
README = pathlib.Path("README.md")
HASH = re.compile(r"-[0-9a-f]{8}$")


def target(path: pathlib.Path) -> pathlib.Path:
    base = HASH.sub("", path.stem)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return path.with_name(f"{base}-{digest}{path.suffix}")


def main() -> None:
    renamed = {}
    for source in sorted(ASSETS.glob("*.svg")):
        destination = target(source)
        if destination == source:
            continue
        if destination.exists():
            destination.unlink()
        source.rename(destination)
        renamed[source.name] = destination.name

    if not renamed:
        print("already hashed")
        return

    if README.exists():
        text = README.read_text()
        for old, new in renamed.items():
            text = text.replace(f"assets/{old}", f"assets/{new}")
        README.write_text(text)
    print(f"hashed {len(renamed)} cards")


if __name__ == "__main__":
    main()
