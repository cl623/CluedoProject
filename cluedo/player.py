"""Player state: identity, hand, board position."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from .cards import Card


@dataclass
class Player:
    """A participant in the game (human hot-seat or simple bot)."""

    name: str
    character: str
    hand: Set[Card] = field(default_factory=set)
    current_room: str = ""

    def holds_any(self, suspect: Card, weapon: Card, room: Card) -> List[Card]:
        """Cards in hand matching the suggestion triple."""
        wanted = {suspect, weapon, room}
        return [c for c in self.hand if c in wanted]
