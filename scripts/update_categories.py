import shutil
import subprocess
from pathlib import Path
from subprocess import run


run(["python", "scripts/scrape_categories.py"], check=True)


def check(new: Path) -> None:
    old = Path("marktplaats") / new

    code = run(
        ["diff", new, old],
        stdout=subprocess.DEVNULL,
    ).returncode

    if code:
        print(f"{new} differs, moving... ", end="", flush=True)
        shutil.move(new, old)
        print("Done")
    else:
        print(f"No difference in {new}, deleting... ", end="", flush=True)
        new.unlink()
        print("Done")


check(Path("l1_categories.json"))
check(Path("l2_categories.json"))
