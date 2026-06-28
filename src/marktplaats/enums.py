from __future__ import annotations

from enum import Enum


class Platform(Enum):
    """Enumeration of the different platforms marktplaats-py supports."""

    MARKTPLAATS = "marktplaats.nl"
    TWEEDEHANDS = "2dehands.be"
