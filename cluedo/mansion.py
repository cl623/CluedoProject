"""Mansion layout: room graph and character starting positions."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set

from .constants import ROOMS, SUSPECTS

# Undirected adjacency (including secret passages).
ROOM_CONNECTIONS: Dict[str, Set[str]] = {
    "Study": {"Hall", "Library", "Kitchen"},  # secret passage to Kitchen
    "Hall": {"Study", "Lounge", "Ballroom", "Billiard Room"},
    "Lounge": {"Hall", "Dining Room", "Conservatory"},  # secret to Conservatory
    "Library": {"Study", "Billiard Room", "Conservatory"},
    "Billiard Room": {"Library", "Hall", "Dining Room", "Ballroom"},
    "Conservatory": {"Library", "Ballroom", "Lounge"},
    "Ballroom": {"Hall", "Billiard Room", "Conservatory", "Kitchen"},
    "Kitchen": {"Ballroom", "Dining Room", "Study"},
    "Dining Room": {"Lounge", "Billiard Room", "Kitchen"},
}


def validate_mansion() -> None:
    for room in ROOMS:
        if room not in ROOM_CONNECTIONS:
            raise ValueError(f"Missing connections for room: {room}")
    for room, neighbors in ROOM_CONNECTIONS.items():
        for n in neighbors:
            if room not in ROOM_CONNECTIONS.get(n, set()):
                raise ValueError(f"Asymmetric edge: {room} -> {n}")


# Each suspect begins in a specific room (simplified from the board’s colored pawns).
STARTING_ROOM: Dict[str, str] = {
    "Miss Scarlett": "Lounge",
    "Colonel Mustard": "Study",
    "Mrs. White": "Ballroom",
    "Mr. Green": "Conservatory",
    "Mrs. Peacock": "Kitchen",
    "Professor Plum": "Library",
}


def neighbors(room: str) -> List[str]:
    return sorted(ROOM_CONNECTIONS[room])


def rooms_within_steps(start: str, max_steps: int) -> Dict[str, int]:
    """Shortest-path distances from start; each edge costs 1 (unweighted BFS)."""
    if max_steps < 0:
        return {}
    dist: Dict[str, int] = {start: 0}
    q: deque[str] = deque([start])
    while q:
        u = q.popleft()
        if dist[u] >= max_steps:
            continue
        for v in ROOM_CONNECTIONS[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


validate_mansion()

# Export for tests / external use
__all__ = ["ROOM_CONNECTIONS", "STARTING_ROOM", "neighbors", "rooms_within_steps"]
