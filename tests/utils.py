from __future__ import annotations

import os
from pathlib import Path


def get_mock_file(name: str) -> str:
    here = Path(os.path.realpath(__file__)).parent
    return (here / "mock" / name).read_text(encoding="utf-8")
