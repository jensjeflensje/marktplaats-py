from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from scripts import scrape_categories


def check(new: Path) -> None:
    old = Path("src/marktplaats") / new

    code = subprocess.run(
        ["diff", new, old],
        stdout=subprocess.DEVNULL,
        check=False,
    ).returncode

    if code:
        print(f"{new} differs, moving... ", end="", flush=True)
        shutil.move(new, old)
        print("Done")
    else:
        print(f"No difference in {new}, deleting... ", end="", flush=True)
        new.unlink()
        print("Done")


def main() -> None:
    scrape_categories.main()

    check(Path("l1_categories.json"))
    check(Path("l2_categories.json"))


if __name__ == "__main__":
    main()
