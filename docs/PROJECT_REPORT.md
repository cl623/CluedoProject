# Cluedo / Clue — Project Report (Draft)

**Course project — digital implementation of Cluedo (Clue)**  
**Status:** Draft for current implementation stage (update before final submission)  
**Repository:** ChristianLaggui_Project2_SourceCode  
**Technology:** Python 3.8+ (standard library); CLI text interface (`main.py`); optional Tkinter UI (`main_tk.py`)

---

## Abstract

We implemented a playable digital version of the classic deduction board game **Cluedo** (*Clue* in North America) in Python. The software models the mansion as a room graph, deals cards, holds a secret murder solution in an envelope, supports dice-based movement, suggestions and clockwise refutation with private card disclosure, optional accusation timing, structured suggestion history, optional per-player deduction sheets, and session logging in CLI mode. We also provide a **hot-seat graphical interface** using Tkinter that guides each turn and separates public vs private information. The goal is to combine game mechanics with clear reasoning support and reliable rule enforcement suitable for demonstration and analysis in an AI / logic-in-games context.

---

## Introduction

Cluedo is a well-known murder-mystery board game: players move through a mansion, gather clues implied by suggestions and refutations, and attempt to infer which **suspect**, **weapon**, and **room** cards are hidden in the solution envelope. Implementing it in software lets us:

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
- Private hand dialogs and suggester-only reveal for refuted cards; public history panel lists suggestions without exposing which card was shown.

---

## Thorough testing

We validate behavior through **manual hot-seat testing**, **deterministic seeds**, and **import/syntax checks**. The table below is a living checklist; replace bracketed placeholders with real screenshots before final PDF export (recommended folder: `docs/assets/`).

| ID | Scenario | Steps | Expected result | Evidence |
|----|----------|-------|-----------------|----------|
| T1 | Import / syntax | Run `python -m compileall -q cluedo ui main.py main_tk.py` | Exit code 0 | `[Screenshot: terminal showing successful compileall]` |
| T2 | Deterministic deal | `python main.py --seed 42` (new game, 3 players, default characters if needed) | Same seed produces repeatable deal for demo | `[Screenshot: CLI showing seed line]` |
| T3 | Movement reach | After roll, only rooms listed with distance ≤ roll are legal | Invalid room rejected | `[Screenshot: movement phase]` |
| T4 | Suggestion + refute order | Three players; suggestion such that a specific downstream player holds a match | Correct refuter responds first | `[Screenshot: suggestion + message]` |
| T5 | Multi-card refute choice | Refuter holds two matching cards | Refuter chooses which to show | `[Screenshot: refute choice / dialog]` |
| T6 | Public vs private info | After suggestion | Non-suggester does not see card identity in shared log view | `[Screenshot: public history vs private dialog]` |
| T7 | Wrong accusation | Intentionally wrong triple | Player eliminated; game continues | `[Screenshot: elimination message]` |
| T8 | Tkinter flow | `python main_tk.py` | Setup → roll → move → suggest works without crash | `[Screenshot: main UI window]` |

**Automated parity smoke (development):** we run a short scripted check of `ui.controller.GameController` with a fixed seed to ensure roll/move/suggest/accusation outcomes remain consistent with the engine. Document exact commands and outputs in an appendix if required by the marker.

---

## Challenges faced

- **Rule fidelity vs UX:** balancing strict rules (refutation order, private information) with clear prompts in CLI and modal dialogs in Tkinter.
- **State management in GUI:** mapping one continuous game into **phases** (when accusation, roll, move, suggestion, end turn are legal) without desynchronizing from `GameEngine`.
- **Incomplete information:** deducing from refutations where non-suggesters do not know **which** card was shown is subtle; we implemented full elimination for the suggester when they see a card, and optional sheet support for their own seat.
- **Hot-seat trust:** physical “look away” remains a social layer; the UI mirrors that by separating public history from private modals.

---

## Stability and reliability

**Strengths**

- Core logic uses the Python standard library only, reducing dependency breakage.
- `GameEngine` centralizes solution, dealing, movement tracking (`last_room_entered`), and refutation discovery (`first_refuter_candidates`), which limits duplicate rule logic between CLI and UI.
- `compileall` and module import checks catch syntax errors early.

**Limitations / risks**

- GUI testing is largely **manual**; we do not ship a full automated harness for Tkinter events in-repo.
- Edge cases (network play, undo, save/load) are **out of scope** for this milestone.
- Long sessions depend on OS/window manager behavior for Tkinter; we recommend short demo runs for the presentation.

**Reliability verdict (draft):** adequate for classroom demonstration and local hot-seat play; we recommend recording a short **screen capture** as backup if live demo hardware fails.

---

## Additional details

### Architecture (high level)

- **`cluedo/`** domain: `constants`, `mansion` (graph + BFS), `cards`, `player`, `engine`, `history`, `deduction`.
- **`main.py`** CLI loop: setup, hands, movement, suggestion, accusations, optional `--sheet` / `--log`.
- **`main_tk.py` + `ui/`** presentation: `GameController` turn phases, dialogs, widgets.

```text
CLI / GUI  ->  GameController (ui) or main.py loop
                    ->  GameEngine + mansion + cards
```

### How to run (summary)

| Mode | Command |
|------|---------|
| CLI | `python main.py` optional `--seed`, `--log`, `--sheet` |
| UI | `python main_tk.py` optional `--seed`, `--log` |

### Future work (optional)

- Richer board visualization (canvas or illustrated map), optional AI bots, save/load, automated UI tests with a harness.

### Exporting this draft to PDF

1. Proofread this file in Markdown.
2. Export via your preferred tool (e.g. Pandoc, Markdown PDF extension, or print from a rendered preview).
3. Insert screenshots into the PDF or inline in the source under `docs/assets/` before final submission.

---

## Document history

| Revision | Date | Notes |
|----------|------|--------|
| 0.1 | (fill in) | Initial draft scaffold; align with current code + assignment sections |

*End of draft.*
