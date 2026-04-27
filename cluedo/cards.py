"""Card types, murder solution envelope, and dealing."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .constants import ROOMS, SUSPECTS, WEAPONS


@dataclass(frozen=True)
class Card:
    """A single clue card (suspect, weapon, or room)."""

    category: str  # "suspect" | "weapon" | "room"
    name: str

    def __str__(self) -> str:
        return self.name


def full_deck() -> List[Card]:
    cards: List[Card] = []
    cards.extend(Card("suspect", s) for s in SUSPECTS)
    cards.extend(Card("weapon", w) for w in WEAPONS)
    cards.extend(Card("room", r) for r in ROOMS)
    return cards


@dataclass
class MurderSolution:
    suspect: Card
    weapon: Card
    room: Card


def draw_secret_solution(deck: Sequence[Card], rng: random.Random) -> Tuple[MurderSolution, List[Card]]:
    """Pick one suspect, one weapon, one room at random; return solution and remaining deck."""
    suspects = [c for c in deck if c.category == "suspect"]
    weapons = [c for c in deck if c.category == "weapon"]
    rooms = [c for c in deck if c.category == "room"]
    s = rng.choice(suspects)
    w = rng.choice(weapons)
    r = rng.choice(rooms)
    solution = MurderSolution(suspect=s, weapon=w, room=r)
    removed = {s, w, r}
    remainder = [c for c in deck if c not in removed]
    rng.shuffle(remainder)
    return solution, remainder


def deal_evenly(cards: Sequence[Card], num_players: int) -> List[List[Card]]:
    """Deal cards as evenly as possible (leftover cards are not used — classic unused pile)."""
    if num_players < 1:
        raise ValueError("num_players must be at least 1")
    piles: List[List[Card]] = [[] for _ in range(num_players)]
    for i, card in enumerate(cards):
        piles[i % num_players].append(card)
    return piles
