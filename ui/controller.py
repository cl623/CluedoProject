"""UI-facing game controller for Tkinter hot-seat gameplay."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from cluedo.cards import Card
from cluedo.constants import ROOMS, SUSPECTS, WEAPONS
from cluedo.deduction import DeductionSheet, sheets_for_players
from cluedo.engine import GameEngine, accusation_matches
from cluedo.history import SuggestionRecord
from cluedo.mansion import neighbors, rooms_within_steps


class TurnPhase(str, Enum):
    PRE_ACCUSATION = "pre_accusation"
    MOVEMENT = "movement"
    ACTIONS = "actions"
    POST_ACTIONS = "post_actions"
    GAME_OVER = "game_over"


@dataclass
class SuggestionOutcome:
    """Outcome for a suggestion including public and private info."""

    record: SuggestionRecord
    shown_card: Optional[Card]


@dataclass
class AccusationOutcome:
    """Outcome from an accusation attempt."""

    status: str  # "continue" | "win" | "eliminated"
    message: str


class GameController:
    """Maintains turn state and bridges UI interactions to core engine."""

    def __init__(self, seed: Optional[int] = None, log_path: Optional[str] = None) -> None:
        self.seed = seed
        self.log_path = log_path
        self.engine: Optional[GameEngine] = None
        self.turn = 0
        self.phase = TurnPhase.PRE_ACCUSATION
        self.last_roll: Optional[int] = None
        self.reachable_map: Dict[str, int] = {}
        self.suggestion_history: List[SuggestionRecord] = []
        self.deduction_sheets: Dict[str, DeductionSheet] = {}

    def setup_new_game(self, player_specs: List[Tuple[str, str]]) -> None:
        self.engine = GameEngine.new_game(player_specs, seed=self.seed)
        self.turn = 1
        self.phase = TurnPhase.PRE_ACCUSATION
        self.last_roll = None
        self.reachable_map = {}
        self.suggestion_history = []
        self.deduction_sheets = sheets_for_players(self.engine.players)
        if self.log_path:
            self._append_session_log([f"=== New session (seed={self.seed!r}) ==="])

    @property
    def has_game(self) -> bool:
        return self.engine is not None

    @property
    def current_player(self):
        if self.engine is None:
            return None
        return self.engine.current_player

    def current_status_line(self) -> str:
        if not self.engine:
            return "No active game."
        p = self.engine.current_player
        return (
            f"Turn {self.turn} | {p.name} ({p.character}) | Room: {p.current_room} | "
            f"Phase: {self.phase.value.replace('_', ' ')}"
        )

    def available_exits(self) -> List[str]:
        if not self.engine:
            return []
        return neighbors(self.engine.current_player.current_room)

    def can_accuse(self) -> bool:
        return self.engine is not None and self.phase in {
            TurnPhase.PRE_ACCUSATION,
            TurnPhase.POST_ACTIONS,
        }

    def can_roll(self) -> bool:
        return self.engine is not None and self.phase == TurnPhase.PRE_ACCUSATION

    def can_move(self) -> bool:
        return self.engine is not None and self.phase == TurnPhase.MOVEMENT

    def can_suggest(self) -> bool:
        if not self.engine or self.phase != TurnPhase.ACTIONS:
            return False
        return self.engine.last_room_entered is not None

    def can_end_turn(self) -> bool:
        return self.engine is not None and self.phase in {TurnPhase.ACTIONS, TurnPhase.POST_ACTIONS}

    def roll_dice(self) -> Tuple[int, Dict[str, int]]:
        if self.engine is None or self.phase != TurnPhase.PRE_ACCUSATION:
            raise RuntimeError("Roll is only allowed at start of turn.")
        roll = self.engine.rng.randint(1, 6) + self.engine.rng.randint(1, 6)
        dist_map = rooms_within_steps(self.engine.current_player.current_room, roll)
        self.last_roll = roll
        self.reachable_map = {r: d for r, d in dist_map.items() if d > 0}
        self.phase = TurnPhase.MOVEMENT
        return roll, dict(self.reachable_map)

    def move_to(self, destination: Optional[str]) -> str:
        if self.engine is None or self.phase != TurnPhase.MOVEMENT:
            raise RuntimeError("Movement is not available yet.")
        if destination is None:
            self.engine.last_room_entered = None
            self.phase = TurnPhase.ACTIONS
            return f"{self.engine.current_player.name} stays in {self.engine.current_player.current_room}."
        if destination not in self.reachable_map:
            raise ValueError("Selected room is not reachable from current roll.")
        self.engine.move_to(destination)
        self.phase = TurnPhase.ACTIONS
        return f"{self.engine.current_player.name} moved to {destination}."

    def skip_suggestion(self) -> None:
        if self.engine is None:
            raise RuntimeError("No active game.")
        self.phase = TurnPhase.POST_ACTIONS

    def suggest(
        self,
        suspect_name: str,
        weapon_name: str,
        choose_card: Callable[[str, List[Card]], Card],
    ) -> SuggestionOutcome:
        if self.engine is None:
            raise RuntimeError("No active game.")
        if not self.can_suggest():
            raise RuntimeError("Suggestion is not available.")
        if suspect_name not in SUSPECTS or weapon_name not in WEAPONS:
            raise ValueError("Invalid suspect or weapon.")

        p = self.engine.current_player
        room_card = Card("room", p.current_room)
        suspect = Card("suspect", suspect_name)
        weapon = Card("weapon", weapon_name)

        idx, candidates = self.engine.first_refuter_candidates(
            self.engine.current_index, suspect, weapon, room_card
        )
        shown: Optional[Card] = None
        refuter_name: Optional[str] = None
        refuter_character: Optional[str] = None
        had_refutation = False
        if candidates:
            had_refutation = True
            responder = self.engine.players[idx]
            refuter_name = responder.name
            refuter_character = responder.character
            shown = choose_card(responder.name, candidates)
            if p.character in self.deduction_sheets and shown is not None:
                self.deduction_sheets[p.character].eliminate_card(shown)

        rec = SuggestionRecord(
            turn=self.turn,
            suggester_name=p.name,
            suggester_character=p.character,
            suspect=suspect_name,
            weapon=weapon_name,
            room=p.current_room,
            refuter_name=refuter_name,
            refuter_character=refuter_character,
            had_refutation=had_refutation,
        )
        self.suggestion_history.append(rec)
        self.phase = TurnPhase.POST_ACTIONS
        self._append_suggestion_log(rec, shown)
        return SuggestionOutcome(record=rec, shown_card=shown)

    def accuse(self, suspect: str, weapon: str, room: str) -> AccusationOutcome:
        if self.engine is None or not self.can_accuse():
            raise RuntimeError("Accusation is not available at this step.")
        p = self.engine.current_player
        if not (suspect in SUSPECTS and weapon in WEAPONS and room in ROOMS):
            raise ValueError("Invalid accusation selection.")
        if accusation_matches(self.engine.solution, suspect, weapon, room):
            self.phase = TurnPhase.GAME_OVER
            return AccusationOutcome(
                status="win",
                message=f"{p.name} wins! The solution was {suspect}, {weapon}, {room}.",
            )

        character = p.character
        idx = self.engine.current_index
        del self.engine.players[idx]
        self.deduction_sheets.pop(character, None)
        if not self.engine.players:
            self.phase = TurnPhase.GAME_OVER
            return AccusationOutcome(
                status="win",
                message="No players remain. The game ends without a winner.",
            )
        if self.engine.current_index >= len(self.engine.players):
            self.engine.current_index = 0
        self.turn += 1
        self.phase = TurnPhase.PRE_ACCUSATION
        self.last_roll = None
        self.reachable_map = {}
        return AccusationOutcome(
            status="eliminated",
            message=f"{p.name}'s accusation was incorrect and they were eliminated.",
        )

    def end_turn(self) -> None:
        if self.engine is None or not self.can_end_turn():
            raise RuntimeError("Cannot end turn now.")
        self.engine.advance_turn()
        self.turn += 1
        self.phase = TurnPhase.PRE_ACCUSATION
        self.last_roll = None
        self.reachable_map = {}

    def deduction_text_for_current(self) -> str:
        if not self.engine:
            return ""
        p = self.engine.current_player
        sheet = self.deduction_sheets.get(p.character)
        if not sheet:
            return "No deduction sheet available."
        return sheet.format_compact()

    def public_history_lines(self) -> List[str]:
        lines: List[str] = []
        for rec in self.suggestion_history:
            line = (
                f"Turn {rec.turn}: {rec.suggester_name} ({rec.suggester_character}) suggested "
                f"{rec.suspect} / {rec.weapon} / {rec.room}."
            )
            if rec.had_refutation:
                line += f" Refuted by {rec.refuter_name} ({rec.refuter_character})."
            else:
                line += " No one could refute."
            lines.append(line)
        return lines

    def _append_suggestion_log(self, rec: SuggestionRecord, shown: Optional[Card]) -> None:
        if not self.log_path:
            return
        pub = (
            f"[Turn {rec.turn}] PUBLIC: {rec.suggester_name} ({rec.suggester_character}) suggested "
            f"{rec.suspect} | {rec.weapon} | {rec.room}. "
        )
        if rec.had_refutation:
            pub += (
                f"Refuted by {rec.refuter_name} ({rec.refuter_character}); "
                "card shown only to suggester."
            )
        else:
            pub += "No refutation."
        lines = [pub]
        if shown is not None:
            lines.append(
                f"  PRIVATE (suggester only): {rec.suggester_name} was shown: "
                f"{shown.name} ({shown.category})"
            )
        self._append_session_log(lines)

    def _append_session_log(self, lines: List[str]) -> None:
        if not self.log_path:
            return
        with open(self.log_path, "a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
