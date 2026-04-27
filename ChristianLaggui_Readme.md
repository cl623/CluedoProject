# Cluedo / Clue — Part 1

Implemented a text-based digital version of the classic murder-mystery game **Cluedo** (known as **Clue** in North America). The program covers mansion layout, six suspects, six weapons, nine rooms, random secret solution, dice-based movement on the room graph, and suggestions with clockwise refutation.

## Prerequisites

- **Python 3.8 or newer** (standard library only; tested on recent 3.x releases).
- **Standard library only** — no third-party packages are required.

## Repository layout

```text
ChristianLaggui_Project2_SourceCode/
  main.py                     # Run the game from here
  ChristianLaggui_Readme.md   # This file
  requirements.txt            # Documents Python version (no pip deps)
  cluedo/
    __init__.py
    constants.py              # Suspects, weapons, rooms
    mansion.py                # Room graph, starting positions, movement (BFS)
    cards.py                  # Deck, secret envelope, dealing
    player.py                 # Player hands and position
    engine.py                 # Game state and refutation order
```
## How to run the game

### 1. Get the source

Extract the zip file and open a terminal in `ChristianLaggui_Project2_SourceCode`.

### 2. Start the game

From inside `ChristianLaggui_Project2_SourceCode`:

```bash
python main.py
```

Optional reproducible card deal (same seed → same hands and solution):

```bash
python main.py --seed 42
```

### 3. Play (hot-seat)

1. Choose **3–6** players and enter each display name.
2. Each player picks a **unique** character (Miss Scarlett, Colonel Mustard, and so on).
3. Each player privately views their dealt cards when prompted.
4. On a turn: the game rolls **two dice**; we may move to any other room reachable along the mansion graph within that many steps, or stay.
5. After **moving into** a room (not when staying put), we may make a **suggestion** (suspect + weapon + current room). Starting to the suggester’s left, the first player who can **refutes** by showing one matching card **only to the suggester** (on one screen, others should look away for that step).
6. We may attempt a **final accusation**; a wrong accusation **eliminates** that player without revealing the envelope.

## Game content (classic set)

- **Suspects:** Miss Scarlett, Colonel Mustard, Mrs. White, Mr. Green, Mrs. Peacock, Professor Plum  
- **Weapons:** Candlestick, Dagger, Lead Pipe, Revolver, Rope, Wrench  
- **Rooms:** Study, Hall, Lounge, Library, Billiard Room, Conservatory, Ballroom, Kitchen, Dining Room  

Starting rooms and door connections follow a simplified classic board layout, including **secret passages** between Study↔Kitchen and Lounge↔Conservatory.

## Troubleshooting

- **`python` not found:** Try `py main.py` on Windows, or install Python from [python.org](https://www.python.org/downloads/).
- **Keyboard interrupt:** `Ctrl+C` exits the game.
