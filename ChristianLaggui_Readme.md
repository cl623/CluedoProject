# Cluedo / Clue — Part 1

Implemented a text-based digital version of the classic murder-mystery game **Cluedo** (known as **Clue** in North America). The program covers mansion layout, six suspects, six weapons, nine rooms, random secret solution, dice-based movement on the room graph, suggestions with clockwise refutation, structured suggestion history, optional session logging, optional deduction sheets, and accusations at more than one point in the turn.

## Prerequisites

- **Python 3.8 or newer** (standard library only; tested on recent 3.x releases).
- **Standard library only** — no third-party packages are required.

## Repository layout

```text
ChristianLaggui_Project2_SourceCode/
  main.py                     # CLI (text mode) entrypoint
  main_tk.py                  # Tkinter UI entrypoint
  ChristianLaggui_Readme.md   # This file
  PRESENTATION.md             # Demo and explanation checklist for markers
  requirements.txt            # Documents Python version (no pip deps)
  cluedo/
    __init__.py
    constants.py              # Suspects, weapons, rooms
    mansion.py                # Room graph, starting positions, movement (BFS)
    cards.py                  # Deck, secret envelope, dealing
    player.py                 # Player hands and position
    engine.py                 # Game state; refutation order (first refuter + candidates)
    history.py                # Structured suggestion/refutation records
    deduction.py              # Per-player envelope elimination sets
  ui/
    __init__.py
    app.py                    # Main Tkinter app frame and setup/game screens
    controller.py             # UI turn-phase controller over game engine
    dialogs.py                # Private/public modal dialogs
    widgets.py                # Reusable status/history/action/board widgets
  docs/
    PROJECT_REPORT.md         # Assignment report draft (export to PDF for submission)
```

## How to run the game

### 1. Get the source

Extract the zip file and open a terminal in `ChristianLaggui_Project2_SourceCode`.

### 2. Start the game

From inside `ChristianLaggui_Project2_SourceCode`.

CLI mode:

```bash
python main.py
```

Tkinter UI mode:

```bash
python main_tk.py
```

Optional reproducible card deal (same seed → same hands and solution):

```bash
python main.py --seed 42
```

Append a human-readable session log (public suggestion lines plus suggester-only card lines):

```bash
python main.py --log cluedo_session.log
```

Print a deduction summary for the active player at the start of each turn:

```bash
python main.py --sheet
```

Flags can be combined, for example:

```bash
python main.py --seed 42 --log cluedo_session.log --sheet
```

UI mode also accepts `--seed` and `--log`:

```bash
python main_tk.py --seed 42 --log cluedo_session.log
```

### 3. Play (hot-seat)

1. Choose **3–6** players and enter each display name.
2. Each player picks a **unique** character (Miss Scarlett, Colonel Mustard, and so on).
3. Each player privately views their dealt cards when prompted.
4. On a turn: we may attempt a **final accusation** before rolling; then the game rolls **two dice**; we may move to any other room reachable along the mansion graph within that many steps, or stay.
5. After **moving into** a room (not when staying put), we may make a **suggestion** (suspect + weapon + current room). Starting to the suggester’s left, the first player who can **refutes** chooses **one** matching card in their hand to show **only to the suggester** (others should look away for that step).
6. After each suggestion, a **public record** is printed (and optionally appended to `--log`) so everyone can track refutations without learning which card was shown.
7. We may attempt a **final accusation** again after the suggestion step; a wrong accusation **eliminates** that player without revealing the envelope.

For a short demo script and talking points, see [PRESENTATION.md](PRESENTATION.md).

## Game content (classic set)

- **Suspects:** Miss Scarlett, Colonel Mustard, Mrs. White, Mr. Green, Mrs. Peacock, Professor Plum  
- **Weapons:** Candlestick, Dagger, Lead Pipe, Revolver, Rope, Wrench  
- **Rooms:** Study, Hall, Lounge, Library, Billiard Room, Conservatory, Ballroom, Kitchen, Dining Room

Starting rooms and door connections follow a simplified classic board layout, including **secret passages** between Study↔Kitchen and Lounge↔Conservatory.

## Troubleshooting

- **`python` not found:** Try `py main.py` on Windows, or install Python from [python.org](https://www.python.org/downloads/).
- **Keyboard interrupt:** `Ctrl+C` exits the game.
