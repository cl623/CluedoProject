# Cluedo / Clue — Project Report (Draft)

**Course project — digital implementation of Cluedo (Clue)**  
**Status:** Draft for current implementation stage (update before final submission)  
**Repository:** ChristianLaggui_Project2_SourceCode  
**Technology:** Python 3.8+ (standard library); CLI text interface (`main.py`); optional Tkinter UI (`main_tk.py`)

---

## Abstract

I implemented a playable digital version of the classic deduction board game **Cluedo** (*Clue* in North America) in Python. The software models the mansion as a room graph, deals cards, holds a secret murder solution in an envelope, supports dice-based movement, suggestions and clockwise refutation with private card disclosure, optional accusation timing, structured suggestion history, optional per-player deduction sheets, and session logging in CLI mode. I also provide a **hot-seat Tkinter interface** with a **clickable node–link map** (rooms and doors from the same graph as the engine), **card-style tiles** (emoji and category colors) for suggestions, accusations, refutation choice, and hand review, plus **deduction chips** and **roll/move hints** in the main window so play is less text-modal and more spatial. The goal is to combine game mechanics with clear reasoning support and reliable rule enforcement suitable for demonstration and analysis in an AI / logic-in-games context.

---

## Introduction

Cluedo is a well-known murder-mystery board game: players move through a mansion, gather clues implied by suggestions and refutations, and attempt to infer which **suspect**, **weapon**, and **room** cards are hidden in the solution envelope. Implementing it in software makes the following possible:

- Encode rules unambiguously and avoid mistakes typical in manual moderation.
- Support **logic and deduction** with structured history and optional elimination tracking.
- Explore **human–computer interaction** via both terminal and GUI for the same underlying rules.

Motivation for this project is to strengthen problem-solving and software design skills while building a self-contained, demo-friendly application without relying on third-party game engines.

---

## Game rules (as implemented)

The implementation follows a **simplified classic** card set and board connectivity (see `cluedo/constants.py` and `cluedo/mansion.py`).

### Setup

- **3–6** players; each chooses a **unique** suspect character.
- The solution is built from **one random suspect, one weapon, one room** placed in a secret envelope.
- Remaining cards are dealt as evenly as possible; those cards are **not** in the envelope.

### Movement

- On a turn, the current player rolls **two six-sided dice** (sum = movement budget).
- Movement is along an **undirected room graph**; the player may move to any room reachable within the roll using shortest-path distance (BFS). They may **stay** instead of moving.

### Suggestions

- If the player **enters a new room** on that turn (not merely staying), they may make a **suggestion**: named suspect + named weapon + **current room**.
- Refutation proceeds **clockwise** starting left of the suggester: the **first** player who holds **any** of those three cards must refute.
- The refuting player chooses **which** of their matching cards to show, if they hold more than one (**only the suggester** sees the card identity in hot-seat play).

### Deduction aids (CLI)

- Optional **`--sheet`**: shows possible envelope cards for the active player based on their hand and cards shown to them as suggester.
- Optional **`--log`**: appends session lines; **public** lines describe who suggested and who refuted; **private** lines record the exact card shown (suggester-only), matching hot-seat fairness.

### Accusations

- A **final accusation** may be offered at **more than one** point in the turn in CLI mode (before rolling and after the suggestion phase).
- **Correct** accusation: that player wins and the solution is revealed.
- **Incorrect** accusation: that player is **eliminated** without revealing the envelope; play continues.

### Tkinter UI (hot-seat)

- Guided actions with buttons enabled only when legal for the current phase.
- **Mansion map** (`ui/board_map.py`): `tk.Canvas` drawing of room nodes and edges from `ROOM_CONNECTIONS`; after a roll, **reachable** rooms are highlighted in green with minimum step counts; the **current** room and **selected** destination use distinct outlines; the player clicks a reachable room then **Move** (or confirms staying put when no selection is valid for that roll).
- **Card tiles** (`ui/theme.py`): each suspect, weapon, and room has a consistent emoji and category tint; used in suggestion and accusation pickers, refutation “show one card,” private reveal, and **scrollable hand** view.
- **Full-tile clicks:** inner `Label` widgets would otherwise absorb mouse events; I bind **Button-1** recursively on the tile root and all children (`bind_tile_button1`) so selection works on the card body, not only the frame edge.
- **Deduction** and **public history** panels use compact chip-style rows and line prefixes for readability.
- **Status line hints** reduce modal pop-ups for routine roll/move guidance.
- Private hand dialogs and suggester-only reveal for refuted cards; public history still lists suggestions without exposing which card was shown.

---

## Thorough testing

I validate behavior through **manual hot-seat testing**, **deterministic seeds**, and **import/syntax checks**. The table below is a living checklist; replace bracketed placeholders with real screenshots before final PDF export (recommended folder: `docs/assets/`).

| ID | Scenario | Steps | Expected result | Evidence |
|----|----------|-------|-----------------|----------|
| T1 | Import / syntax | Run `python -m compileall -q cluedo ui main.py main_tk.py` | Exit code 0 | `[Screenshot: terminal showing successful compileall]` |
| T2 | Deterministic deal | `python main.py --seed 42` (new game, 3 players, default characters if needed) | Same seed produces repeatable deal for demo | `[Screenshot: CLI showing seed line]` |
| T3 | Movement reach | After roll, only graph-reachable rooms within distance ≤ roll are legal (CLI list or UI map) | Invalid destination rejected | `[Screenshot: movement phase — CLI or map]` |
| T4 | Suggestion + refute order | Three players; suggestion such that a specific downstream player holds a match | Correct refuter responds first | `[Screenshot: suggestion + message]` |
| T5 | Multi-card refute choice | Refuter holds two matching cards | Refuter chooses which to show | `[Screenshot: refute choice / dialog]` |
| T6 | Public vs private info | After suggestion | Non-suggester does not see card identity in shared log view | `[Screenshot: public history vs private dialog]` |
| T7 | Wrong accusation | Intentionally wrong triple | Player eliminated; game continues | `[Screenshot: elimination message]` |
| T8 | Tkinter flow | `python main_tk.py` | Setup → roll → move → suggest works without crash | `[Screenshot: main UI window]` |
| T9 | Map + tiles | After roll in UI | Green reachable rooms on map; card tiles in suggestion dialog | `[Screenshot: map with highlights + tile picker]` |
| T10 | Tile hit targets | Open suggestion, accusation, or refute dialog | Clicking center of a card tile selects it (not only the border) | `[Screenshot: selected tile with thick border]` |
| T11 | Private reveal | After refutation with card shown | Large tile; tap on card or OK dismisses | `[Screenshot: private card dialog]` |

**Automated parity smoke (development):** I run a short scripted check of `ui.controller.GameController` with a fixed seed to ensure roll/move/suggest/accusation outcomes remain consistent with the engine. Document exact commands and outputs in an appendix if required by the marker.

---

## Challenges faced

- **Rule fidelity vs UX:** balancing strict rules (refutation order, private information) with clear prompts in CLI and modal dialogs in Tkinter.
- **State management in GUI:** mapping one continuous game into **phases** (when accusation, roll, move, suggestion, end turn are legal) without desynchronizing from `GameEngine`.
- **Incomplete information:** deducing from refutations where non-suggesters do not know **which** card was shown is subtle; I implemented full elimination for the suggester when they see a card, and optional sheet support for their own seat.
- **Hot-seat trust:** physical “look away” remains a social layer; the UI mirrors that by separating public history from private modals.
- **Tkinter pointer routing:** layered `Label`/`Frame` widgets meant card tiles appeared unresponsive unless the player clicked thin borders; I addressed this by **recursive** `Button-1` bindings on every descendant of each tile (`bind_tile_button1`).
- **Canvas layout:** the map redraws on window resize; room labels and hit radii depend on canvas size—I validate on representative window sizes during manual testing.

---

## Stability and reliability

**Strengths**

- Core logic uses the Python standard library only, reducing dependency breakage.
- `GameEngine` centralizes solution, dealing, movement tracking (`last_room_entered`), and refutation discovery (`first_refuter_candidates`), which limits duplicate rule logic between CLI and UI.
- `compileall` and module import checks catch syntax errors early.

**Limitations / risks**

- GUI testing is largely **manual**; I do not ship a full automated harness for Tkinter events in-repo.
- Edge cases (network play, undo, save/load) are **out of scope** for this milestone.
- Long sessions depend on OS/window manager behavior for Tkinter; short demo runs are preferable for the presentation.

**Reliability verdict (draft):** adequate for classroom demonstration and local hot-seat play; recording a short **screen capture** is a sensible backup if live demo hardware fails.

---

## Additional details

### Architecture (high level)

- **`cluedo/`** domain: `constants`, `mansion` (graph + BFS), `cards`, `player`, `engine`, `history`, `deduction`.
- **`main.py`** CLI loop: setup, hands, movement, suggestion, accusations, optional `--sheet` / `--log`.
- **`main_tk.py` + `ui/`** presentation: `GameController` turn phases; `app` layout; **`board_map`** (Canvas map); **`theme`** (tiles + recursive click bind); **`dialogs`** (tiles for hand / suggest / accuse / refute); **`widgets`** (status, actions, deduction chips, history).

```text
CLI / GUI  ->  GameController (ui) or main.py loop
                    ->  GameEngine + mansion + cards
Tk map     ->  ROOM_CONNECTIONS (same edges as movement BFS)
```

- **Supporting doc for ongoing report updates:** narrative instructions for refreshes live in **`docs/skills/cluedo-project-report/SKILL.md`** (project convention; PDF export still targets this `PROJECT_REPORT.md` file).

### How to run (summary)

| Mode | Command |
|------|---------|
| CLI | `python main.py` optional `--seed`, `--log`, `--sheet` |
| UI | `python main_tk.py` optional `--seed`, `--log` |

### Future work (optional)

- Illustrated floor plan art, zoom/pan on the map, optional AI bots, save/load, and automated Tk event tests with a harness.

### Exporting this draft to PDF

1. Proofread this file in Markdown.
2. Export via Pandoc, a Markdown PDF extension, print from a rendered preview, or another preferred workflow.
3. Insert screenshots into the PDF or inline in the source under `docs/assets/` before final submission.

---

## Document history

| Revision | Date | Notes |
|----------|------|--------|
| 0.1 | (fill in) | Initial draft scaffold; align with current code + assignment sections |
| 0.2 | 2026-05 | Visual Tkinter UI: map, card tiles, chips, `bind_tile_button1`; testing rows T10–T11; architecture and challenges |

*End of draft.*
