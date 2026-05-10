"""Modal dialogs used by the Tkinter Cluedo UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Iterable, List, Optional, Sequence, Tuple

from cluedo.cards import Card


def show_hand_dialog(parent: tk.Misc, player_name: str, character: str, hand: Iterable[Card]) -> None:
    cards = sorted((c.category, c.name) for c in hand)
    lines = [f"{name} ({category})" for category, name in cards]
    if not lines:
        lines = ["(no cards)"]
    messagebox.showinfo(
        title=f"Hand for {player_name}",
        message=f"{player_name} as {character}\n\n" + "\n".join(lines),
        parent=parent,
    )


def show_private_card_dialog(parent: tk.Misc, suggester_name: str, card: Card) -> None:
    messagebox.showinfo(
        title="Private Card Reveal",
        message=(
            f"{suggester_name} only:\n\n"
            f"You were shown {card.name} ({card.category}).\n"
            "Other players should not view this dialog."
        ),
        parent=parent,
    )


def choose_refute_card_dialog(
    parent: tk.Misc,
    responder_name: str,
    candidates: List[Card],
) -> Card:
    if len(candidates) == 1:
        return candidates[0]

    top = tk.Toplevel(parent)
    top.title("Choose Card to Show")
    top.transient(parent.winfo_toplevel())
    top.grab_set()
    ttk.Label(
        top,
        text=f"{responder_name}: choose one card to show privately",
        justify="left",
    ).pack(padx=12, pady=(10, 8), anchor="w")

    selected: tk.StringVar = tk.StringVar(value=f"{candidates[0].category}:{candidates[0].name}")
    for c in candidates:
        value = f"{c.category}:{c.name}"
        ttk.Radiobutton(
            top,
            text=f"{c.name} ({c.category})",
            value=value,
            variable=selected,
        ).pack(anchor="w", padx=12, pady=2)

    choice: List[Optional[Card]] = [None]

    def on_ok() -> None:
        raw = selected.get()
        category, name = raw.split(":", 1)
        for c in candidates:
            if c.category == category and c.name == name:
                choice[0] = c
                break
        top.destroy()

    ttk.Button(top, text="Show This Card", command=on_ok).pack(pady=10)
    top.wait_window()
    if choice[0] is None:
        return candidates[0]
    return choice[0]


def choose_two_fields_dialog(
    parent: tk.Misc,
    title: str,
    left_label: str,
    left_values: Sequence[str],
    right_label: str,
    right_values: Sequence[str],
) -> Optional[Tuple[str, str]]:
    top = tk.Toplevel(parent)
    top.title(title)
    top.transient(parent.winfo_toplevel())
    top.grab_set()

    ttk.Label(top, text=left_label).grid(row=0, column=0, padx=8, pady=(8, 2), sticky="w")
    left_var = tk.StringVar(value=left_values[0] if left_values else "")
    left_combo = ttk.Combobox(top, textvariable=left_var, values=list(left_values), state="readonly")
    left_combo.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")

    ttk.Label(top, text=right_label).grid(row=0, column=1, padx=8, pady=(8, 2), sticky="w")
    right_var = tk.StringVar(value=right_values[0] if right_values else "")
    right_combo = ttk.Combobox(top, textvariable=right_var, values=list(right_values), state="readonly")
    right_combo.grid(row=1, column=1, padx=8, pady=(0, 8), sticky="ew")

    result: List[Optional[Tuple[str, str]]] = [None]

    def on_ok() -> None:
        result[0] = (left_var.get(), right_var.get())
        top.destroy()

    def on_cancel() -> None:
        top.destroy()

    btns = ttk.Frame(top)
    btns.grid(row=2, column=0, columnspan=2, pady=(0, 10))
    ttk.Button(btns, text="OK", command=on_ok).pack(side="left", padx=6)
    ttk.Button(btns, text="Cancel", command=on_cancel).pack(side="left", padx=6)

    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=1)
    top.wait_window()
    return result[0]


def choose_accusation_dialog(
    parent: tk.Misc,
    suspects: Sequence[str],
    weapons: Sequence[str],
    rooms: Sequence[str],
) -> Optional[Tuple[str, str, str]]:
    top = tk.Toplevel(parent)
    top.title("Final Accusation")
    top.transient(parent.winfo_toplevel())
    top.grab_set()

    vars_ = [tk.StringVar(value=opts[0] if opts else "") for opts in (suspects, weapons, rooms)]
    labels = ("Suspect", "Weapon", "Room")
    values = (suspects, weapons, rooms)
    for i, (label, var, opts) in enumerate(zip(labels, vars_, values)):
        ttk.Label(top, text=label).grid(row=0, column=i, padx=8, pady=(8, 2), sticky="w")
        combo = ttk.Combobox(top, textvariable=var, values=list(opts), state="readonly")
        combo.grid(row=1, column=i, padx=8, pady=(0, 8), sticky="ew")

    result: List[Optional[Tuple[str, str, str]]] = [None]

    def on_ok() -> None:
        result[0] = (vars_[0].get(), vars_[1].get(), vars_[2].get())
        top.destroy()

    def on_cancel() -> None:
        top.destroy()

    btns = ttk.Frame(top)
    btns.grid(row=2, column=0, columnspan=3, pady=(0, 10))
    ttk.Button(btns, text="Accuse", command=on_ok).pack(side="left", padx=6)
    ttk.Button(btns, text="Cancel", command=on_cancel).pack(side="left", padx=6)
    for i in range(3):
        top.columnconfigure(i, weight=1)
    top.wait_window()
    return result[0]
