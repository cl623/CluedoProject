"""Per-player elimination sets for envelope cards (standard library only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from .cards import Card
from .constants import ROOMS, SUSPECTS, WEAPONS
from .player import Player


@dataclass
class DeductionSheet:
    """Cards that might still be in the murder envelope for this seat."""

    possible_suspects: Set[str] = field(default_factory=set)
    possible_weapons: Set[str] = field(default_factory=set)
    possible_rooms: Set[str] = field(default_factory=set)

    @classmethod
    def from_hand(cls, hand: Set[Card]) -> DeductionSheet:
        """Any card in hand cannot be in the envelope."""
        ps = set(SUSPECTS) - {c.name for c in hand if c.category == "suspect"}
        pw = set(WEAPONS) - {c.name for c in hand if c.category == "weapon"}
        pr = set(ROOMS) - {c.name for c in hand if c.category == "room"}
        return cls(possible_suspects=ps, possible_weapons=pw, possible_rooms=pr)

    def eliminate_card(self, card: Card) -> None:
        """Learn that this card is not in the envelope."""
        if card.category == "suspect":
            self.possible_suspects.discard(card.name)
        elif card.category == "weapon":
            self.possible_weapons.discard(card.name)
        elif card.category == "room":
            self.possible_rooms.discard(card.name)

    def format_compact(self) -> str:
        lines = [
            f"  Suspects still possible ({len(self.possible_suspects)}): {', '.join(sorted(self.possible_suspects))}",
            f"  Weapons still possible ({len(self.possible_weapons)}): {', '.join(sorted(self.possible_weapons))}",
            f"  Rooms still possible ({len(self.possible_rooms)}): {', '.join(sorted(self.possible_rooms))}",
        ]
        return "\n".join(lines)


def sheets_for_players(players: List[Player]) -> Dict[str, DeductionSheet]:
    """One sheet per character name (stable if seating order changes)."""
    return {p.character: DeductionSheet.from_hand(p.hand) for p in players}
