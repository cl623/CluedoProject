"""Game loop: movement, suggestions, refutations."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .cards import Card, MurderSolution, deal_evenly, draw_secret_solution, full_deck
from .constants import ROOMS, SUSPECTS, WEAPONS
from .mansion import STARTING_ROOM, neighbors
from .player import Player


@dataclass
class GameEngine:
    solution: MurderSolution
    players: List[Player]
    rng: random.Random
    current_index: int = 0
    last_room_entered: Optional[str] = None  # set when a move ends in a new room

    @classmethod
    def new_game(cls, player_specs: List[Tuple[str, str]], seed: Optional[int] = None) -> "GameEngine":
        """
        player_specs: list of (display_name, character_name) for each seat.
        Characters must be unique and subset of SUSPECTS.
        """
        rng = random.Random(seed)
        deck = full_deck()
        solution, remainder = draw_secret_solution(deck, rng)
        n = len(player_specs)
        hands = deal_evenly(remainder, n)
        players: List[Player] = []
        for ( pname, character), pile in zip(player_specs, hands):
            if character not in SUSPECTS:
                raise ValueError(f"Unknown character: {character}")
            room = STARTING_ROOM[character]
            players.append(Player(name=pname, character=character, hand=set(pile), current_room=room))
        return cls(solution=solution, players=players, rng=rng)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_index]

    def advance_turn(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.players)
        self.last_room_entered = None

    def move_to(self, room: str) -> None:
        p = self.current_player
        prev = p.current_room
        p.current_room = room
        if room != prev:
            self.last_room_entered = room

    def refute_suggestion(
        self, suggester_index: int, suspect: Card, weapon: Card, room: Card
    ) -> Tuple[Optional[int], Optional[Card]]:
        """
        Starting left of suggester, first player who can show one matching card does.
        Returns (responder_index, card_shown) or (None, None).
        """
        n = len(self.players)
        order = [(suggester_index + 1 + k) % n for k in range(n - 1)]
        for idx in order:
            cand = self.players[idx].holds_any(suspect, weapon, room)
            if cand:
                # Shown card choice: random among valid (simple “AI”); human picks in CLI.
                card = self.rng.choice(cand)
                return idx, card
        return None, None


def format_mansion_help() -> str:
    lines = ["Mansion rooms and exits:"]
    for r in ROOMS:
        ns = ", ".join(neighbors(r))
        lines.append(f"  • {r}: {ns}")
    lines.append("")
    lines.append("Starting room per character:")
    for ch in SUSPECTS:
        lines.append(f"  • {ch}: {STARTING_ROOM[ch]}")
    return "\n".join(lines)


def accusation_matches(solution: MurderSolution, suspect: str, weapon: str, room: str) -> bool:
    return (
        solution.suspect.name == suspect
        and solution.weapon.name == weapon
        and solution.room.name == room
    )


