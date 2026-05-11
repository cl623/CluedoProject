"""Structured log of suggestions and refutations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SuggestionRecord:
    """One suggestion and its public refutation outcome."""

    turn: int
    suggester_name: str
    suggester_character: str
    suspect: str
    weapon: str
    room: str
    refuter_name: Optional[str]
    refuter_character: Optional[str]
    """Who refuted, if anyone. Other players do not learn which card was shown."""
    had_refutation: bool
