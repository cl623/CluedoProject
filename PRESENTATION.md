# Presentation notes (demo and marking)

We use this checklist when demonstrating the project and explaining design choices to markers.

## Setup for a stable demo

- Run from the project folder: `python main.py --seed 42` so the secret envelope and hands are reproducible.
- Optional: `python main.py --seed 42 --log cluedo_session.log` to show that every suggestion is appended to a session file with a **public** line (who suggested what, who refuted) and a **private** line (exact card shown) only for the suggester’s record in the file.
- Optional: `python main.py --seed 42 --sheet` to show per-turn **deduction sheets**: possible envelope cards for the active player, updated when they are shown a refutation card.

## Storyline (what to say in ~2–5 minutes)

1. **Goal:** Deduce the one suspect, one weapon, and one room in the murder envelope; other cards are dealt (or unused in the classic unused pile—here we deal the remainder evenly).
2. **Board model:** Rooms and doors live in `cluedo/mansion.py` as a graph; movement uses BFS to list rooms reachable within the dice roll.
3. **Suggestions:** After moving into a new room, the current player may suggest a suspect, weapon, and that room. Refutation runs **clockwise** from the suggester’s left; the first player who holds any of the three cards must show **exactly one** of those cards to the suggester only. If they hold more than one, **they choose** which to show (implemented in the CLI).
4. **Information and fairness:** After each suggestion, the game prints a **public recap** everyone can note. The log file separates public facts from the suggester-only card identity.
5. **Deduction aid:** With `--sheet`, each player sees remaining envelope candidates for their seat at the start of their turn, based on their hand and any card shown to them as suggester.
6. **Accusations:** A player may accuse **before moving** on their turn or **after** the suggestion step (or after skipping a suggestion when they did not enter a new room). A wrong accusation eliminates that player.

## Live walkthrough tips

- Narrate one full turn: optional accusation, roll and move, optional suggestion, public recap, optional accusation.
- Mention **standard library only** and the module split (`engine`, `cards`, `mansion`, `history`, `deduction`).
- If asked about AI: refutation order is deterministic; deduction uses simple elimination over finite card sets; a future extension could add automated players or constraint propagation from partial refutation knowledge.
