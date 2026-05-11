#!/usr/bin/env python3
"""
Cluedo / Clue — text-based game entry point.

Run: python main.py
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional, Tuple

from cluedo.cards import Card
from cluedo.constants import ROOMS, SUSPECTS, WEAPONS
from cluedo.deduction import DeductionSheet, sheets_for_players
from cluedo.engine import GameEngine, accusation_matches, format_mansion_help
from cluedo.history import SuggestionRecord
from cluedo.mansion import neighbors, rooms_within_steps


def prompt_line(msg: str) -> str:
    try:
        return input(msg).strip()
    except EOFError:
        return ""


def choose_int(msg: str, lo: int, hi: int, default: Optional[int] = None) -> int:
    while True:
        raw = prompt_line(msg)
        if raw == "" and default is not None:
            return default
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print(f"Please enter an integer between {lo} and {hi}.")


def setup_players() -> List[Tuple[str, str]]:
    print("\n=== New game setup ===\n")
    n = choose_int("How many players (3–6)? ", 3, 6)
    specs: List[Tuple[str, str]] = []
    print("\nAssign characters (unique). Default order follows classic suspects list.\n")
    available = list(SUSPECTS)
    for i in range(n):
        name = prompt_line(f"Player {i + 1} display name: ") or f"Player {i + 1}"
        print("Available characters:")
        for j, ch in enumerate(available, start=1):
            print(f"  {j}. {ch}")
        idx = choose_int(f"Pick character number for {name} (1–{len(available)}): ", 1, len(available))
        character = available.pop(idx - 1)
        specs.append((name, character))
    return specs


def reveal_hands(engine: GameEngine) -> None:
    print("\n--- Dealing cards (look away if it is not your seat) ---\n")
    for p in engine.players:
        prompt_line(f"[{p.name} as {p.character}] Press Enter to view your hand...")
        hand_list = sorted((c.category, c.name) for c in p.hand)
        if not hand_list:
            print("  (no cards in hand — unusual but valid)\n")
        else:
            for cat, nm in hand_list:
                print(f"  • {nm} ({cat})")
        print()


def append_session_log(path: str, lines: List[str]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def movement_phase(engine: GameEngine) -> None:
    p = engine.current_player
    roll = engine.rng.randint(1, 6) + engine.rng.randint(1, 6)
    print(f"\n{p.name} ({p.character}) rolls the dice: {roll}")
    dist_map = rooms_within_steps(p.current_room, roll)
    reachable = sorted((r, d) for r, d in dist_map.items() if d > 0)
    if not reachable:
        print("No adjacent movement possible with this roll; you stay in place.")
        engine.last_room_entered = None
        return
    print(f"You are in: {p.current_room}")
    print("Rooms you can reach this turn (with minimum steps):")
    for r, d in reachable:
        print(f"  {d} steps → {r}")
    stay = prompt_line("Stay in your room? [y/N]: ").lower() in {"y", "yes"}
    if stay:
        print("You stay.")
        engine.last_room_entered = None
        return
    names = [r for r, _ in reachable]
    while True:
        dest = prompt_line(f"Move to which room? ({', '.join(names[:5])}...) ").strip()
        if dest in dist_map and dist_map[dest] > 0:
            engine.move_to(dest)
            print(f"You move to {dest}.")
            return
        print("Invalid choice; type the full room name from the list above.")


def pick_from_list(title: str, options: Tuple[str, ...], default: Optional[str] = None) -> str:
    print(title)
    for i, o in enumerate(options, start=1):
        print(f"  {i}. {o}")
    while True:
        raw = prompt_line("Enter number or exact name: ").strip()
        if raw == "" and default is not None:
            return default
        if raw.isdigit():
            k = int(raw)
            if 1 <= k <= len(options):
                return options[k - 1]
        if raw in options:
            return raw
        print("Invalid selection.")


def pick_matching_card_to_show(responder_name: str, candidates: List[Card]) -> Card:
    if len(candidates) == 1:
        return candidates[0]
    print(f"\n[{responder_name}] You must show exactly one card to the suggester. Choose which:")
    for i, c in enumerate(candidates, start=1):
        print(f"  {i}. {c.name} ({c.category})")
    while True:
        raw = prompt_line("Enter number or exact card name: ").strip()
        if raw.isdigit():
            k = int(raw)
            if 1 <= k <= len(candidates):
                return candidates[k - 1]
        for c in candidates:
            if raw == c.name or raw.lower() == c.name.lower():
                return c
        print("Invalid choice.")


def print_public_recap(rec: SuggestionRecord) -> None:
    print("\n--- Public record (everyone may note this) ---")
    print(
        f"Turn {rec.turn}: {rec.suggester_name} ({rec.suggester_character}) suggested "
        f"{rec.suspect} / {rec.weapon} / {rec.room}."
    )
    if not rec.had_refutation:
        print("  No player refuted (no one held any of those three cards).")
    else:
        assert rec.refuter_name is not None and rec.refuter_character is not None
        print(
            f"  {rec.refuter_name} ({rec.refuter_character}) refuted and showed one card "
            f"to {rec.suggester_name} only (others do not see which card)."
        )
    print("--- End public record ---\n")


def suggestion_phase(
    engine: GameEngine,
    turn: int,
    history: List[SuggestionRecord],
    log_path: Optional[str],
    deduction_sheets: Dict[str, DeductionSheet],
) -> None:
    if engine.last_room_entered is None:
        return
    p = engine.current_player
    room_card = Card("room", p.current_room)
    print(f"\nYou entered {p.current_room}. You may make a suggestion.")
    do = prompt_line("Make a suggestion? [Y/n]: ").lower() in {"", "y", "yes"}
    if not do:
        return

    suspect_name = pick_from_list("Suspect to suggest:", SUSPECTS)
    weapon_name = pick_from_list("Weapon to suggest:", WEAPONS)
    print(f"Room for this suggestion is your current room: {p.current_room}")

    suspect = Card("suspect", suspect_name)
    weapon = Card("weapon", weapon_name)

    print(
        f"\n{p.name} suggests: It was {suspect_name} in the {p.current_room} with the {weapon_name}."
    )
    idx, candidates = engine.first_refuter_candidates(
        engine.current_index, suspect, weapon, room_card
    )
    shown: Optional[Card] = None
    refuter_name: Optional[str] = None
    refuter_character: Optional[str] = None
    had_refutation = False

    if not candidates:
        print("No one could refute your suggestion.")
    else:
        had_refutation = True
        responder = engine.players[idx]
        refuter_name = responder.name
        refuter_character = responder.character
        shown = pick_matching_card_to_show(responder.name, candidates)
        print(f"{responder.name} shows a card to {p.name} (privately).")
        prompt_line(f"[{p.name}] Press Enter to see the card shown to you...")
        print(f"  Shown card: {shown.name} ({shown.category})")
        if p.character in deduction_sheets and shown is not None:
            deduction_sheets[p.character].eliminate_card(shown)
        if idx != engine.current_index:
            prompt_line("[Everyone else] Press Enter when ready...")

    rec = SuggestionRecord(
        turn=turn,
        suggester_name=p.name,
        suggester_character=p.character,
        suspect=suspect_name,
        weapon=weapon_name,
        room=p.current_room,
        refuter_name=refuter_name,
        refuter_character=refuter_character,
        had_refutation=had_refutation,
    )
    history.append(rec)
    print_public_recap(rec)

    if log_path:
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
        append_session_log(log_path, lines)


def accusation_option(engine: GameEngine, deduction_sheets: Dict[str, DeductionSheet]) -> str:
    """
    Returns:
        'win' — game over (correct accusation, or no players left).
        'continue' — advance to the next player as usual.
        'eliminated' — current player removed; turn does not advance (next seat is already current).
    """
    p = engine.current_player
    if prompt_line("\nMake a final accusation (risk elimination)? [y/N]: ").lower() not in {"y", "yes"}:
        return "continue"
    s = pick_from_list("Suspect:", SUSPECTS)
    w = pick_from_list("Weapon:", WEAPONS)
    r = pick_from_list("Room:", ROOMS)
    if accusation_matches(engine.solution, s, w, r):
        print(f"\n{p.name} wins! The solution was {s}, {w}, {r}.")
        return "win"
    print(f"\n{p.name}'s accusation is incorrect and they are eliminated from play.")
    ch = p.character
    idx = engine.current_index
    del engine.players[idx]
    deduction_sheets.pop(ch, None)
    if not engine.players:
        print("No players remain. The game ends without a winner.")
        return "win"
    if engine.current_index >= len(engine.players):
        engine.current_index = 0
    return "eliminated"


def play(seed: Optional[int], log_path: Optional[str], show_sheet: bool) -> int:
    print("Cluedo / Clue (text mode)")
    print("=" * 50)
    if seed is not None:
        print(f"Random seed: {seed}")
    if log_path:
        print(f"Session log (append): {log_path}")
    if show_sheet:
        print("Deduction sheet: on (printed at start of each turn for the active player).")

    specs = setup_players()
    engine = GameEngine.new_game(specs, seed=seed)
    reveal_hands(engine)

    deduction_sheets = sheets_for_players(engine.players)
    suggestion_history: List[SuggestionRecord] = []

    print(format_mansion_help())
    print("The murder envelope holds one suspect, one weapon, and one room.\n")

    if log_path:
        append_session_log(
            log_path,
            [f"=== New session (seed={seed!r}) ==="],
        )

    turn = 0
    while True:
        turn += 1
        p = engine.current_player
        print(f"\n--- Turn {turn}: {p.name} playing as {p.character} ---")
        print(f"Location: {p.current_room}")
        print(f"Exits: {', '.join(neighbors(p.current_room))}")

        if show_sheet and p.character in deduction_sheets:
            print("\n--- Deduction sheet (cards that might still be in the envelope) ---")
            print(deduction_sheets[p.character].format_compact())
            print("---\n")

        outcome = accusation_option(engine, deduction_sheets)
        if outcome == "win":
            return 0
        if outcome == "eliminated":
            continue

        movement_phase(engine)

        suggestion_phase(engine, turn, suggestion_history, log_path, deduction_sheets)

        outcome = accusation_option(engine, deduction_sheets)
        if outcome == "win":
            return 0
        if outcome == "eliminated":
            continue
        if outcome == "continue":
            engine.advance_turn()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Cluedo / Clue text game")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible deals")
    parser.add_argument(
        "--log",
        metavar="FILE",
        default=None,
        help="Append human-readable suggestion/refutation lines to this file",
    )
    parser.add_argument(
        "--sheet",
        action="store_true",
        help="Print each active player's deduction possibilities at the start of their turn",
    )
    args = parser.parse_args(argv)
    try:
        return play(args.seed, args.log, args.sheet)
    except KeyboardInterrupt:
        print("\nGame aborted.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
