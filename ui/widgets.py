"""Reusable Tkinter widgets for the Cluedo UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional, Set


class StatusPanel(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.status_var = tk.StringVar(value="No active game.")
        self.roll_var = tk.StringVar(value="Roll: -")
        ttk.Label(self, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=6, pady=(4, 2)
        )
        ttk.Label(self, textvariable=self.roll_var).pack(anchor="w", padx=6, pady=(0, 4))

    def set_status(self, text: str, roll: Optional[int]) -> None:
        self.status_var.set(text)
        if roll is None:
            self.roll_var.set("Roll: -")
        else:
            self.roll_var.set(f"Roll: {roll}")


class ActionPanel(ttk.LabelFrame):
    def __init__(
        self,
        parent: tk.Misc,
        on_accuse: Callable[[], None],
        on_roll: Callable[[], None],
        on_move: Callable[[], None],
        on_suggest: Callable[[], None],
        on_end_turn: Callable[[], None],
        on_show_hand: Callable[[], None],
        on_export_log: Callable[[], None],
    ) -> None:
        super().__init__(parent, text="Actions")
        self.buttons: Dict[str, ttk.Button] = {}
        items = [
            ("Accuse", on_accuse, "accuse"),
            ("Roll Dice", on_roll, "roll"),
            ("Move", on_move, "move"),
            ("Suggest", on_suggest, "suggest"),
            ("End Turn", on_end_turn, "end_turn"),
            ("Show Hand", on_show_hand, "show_hand"),
            ("Export History", on_export_log, "export"),
        ]
        for i, (label, command, key) in enumerate(items):
            btn = ttk.Button(self, text=label, command=command)
            btn.grid(row=i // 2, column=i % 2, sticky="ew", padx=6, pady=6)
            self.buttons[key] = btn
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def set_enabled(self, key: str, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.buttons[key].configure(state=state)


class HistoryPanel(ttk.LabelFrame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, text="Public History")
        self.text = tk.Text(self, height=14, width=80, wrap="word", state="disabled")
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set_lines(self, lines: List[str]) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        for line in lines:
            self.text.insert("end", line + "\n")
        self.text.configure(state="disabled")


class DeductionPanel(ttk.LabelFrame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, text="Current Player Deduction")
        self.label = ttk.Label(self, text="", justify="left")
        self.label.pack(fill="x", padx=6, pady=6)

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)


class BoardPanel(ttk.LabelFrame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, text="Rooms")
        self.listbox = tk.Listbox(self, height=12)
        self.listbox.pack(fill="both", expand=True, padx=6, pady=6)
        self.reachable_rooms: Set[str] = set()

    def set_rooms(
        self,
        rooms: List[str],
        current_room: Optional[str],
        reachable: Dict[str, int],
    ) -> None:
        self.reachable_rooms = set(reachable.keys())
        self.listbox.delete(0, "end")
        for room in rooms:
            marker = ""
            if current_room == room:
                marker = "[Current] "
            elif room in reachable:
                marker = f"[{reachable[room]}] "
            self.listbox.insert("end", f"{marker}{room}")

    def selected_room(self) -> Optional[str]:
        sel = self.listbox.curselection()
        if not sel:
            return None
        raw = self.listbox.get(sel[0])
        if "] " in raw:
            return raw.split("] ", 1)[1]
        return raw
