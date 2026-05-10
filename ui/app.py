"""Tkinter app shell for Cluedo hot-seat UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional, Tuple

from cluedo.constants import ROOMS, SUSPECTS, WEAPONS
from ui.controller import GameController, SuggestionOutcome, TurnPhase
from ui.dialogs import (
    choose_accusation_dialog,
    choose_refute_card_dialog,
    choose_two_fields_dialog,
    show_hand_dialog,
    show_private_card_dialog,
)
from ui.widgets import ActionPanel, BoardPanel, DeductionPanel, HistoryPanel, StatusPanel


class CluedoApp(ttk.Frame):
    def __init__(self, root: tk.Tk, seed: Optional[int] = None, log_path: Optional[str] = None) -> None:
        super().__init__(root)
        self.root = root
        self.controller = GameController(seed=seed, log_path=log_path)
        self.player_count_var = tk.IntVar(value=3)
        self.setup_name_vars: List[tk.StringVar] = []
        self.setup_character_vars: List[tk.StringVar] = []
        self.status_panel: Optional[StatusPanel] = None
        self.action_panel: Optional[ActionPanel] = None
        self.history_panel: Optional[HistoryPanel] = None
        self.deduction_panel: Optional[DeductionPanel] = None
        self.board_panel: Optional[BoardPanel] = None

        self.pack(fill="both", expand=True)
        self._build_setup_screen()

    def _build_setup_screen(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        setup = ttk.LabelFrame(self, text="New Game Setup")
        setup.pack(fill="x", padx=10, pady=10)
        ttk.Label(
            setup,
            text="Choose player count, names, and unique characters.",
        ).grid(row=0, column=0, columnspan=3, padx=8, pady=(8, 4), sticky="w")

        ttk.Label(setup, text="Players (3-6):").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        spin = ttk.Spinbox(
            setup,
            from_=3,
            to=6,
            textvariable=self.player_count_var,
            width=5,
            command=self._refresh_player_rows,
        )
        spin.grid(row=1, column=1, padx=8, pady=6, sticky="w")

        self.rows_container = ttk.Frame(setup)
        self.rows_container.grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=6)
        setup.columnconfigure(2, weight=1)

        ttk.Button(setup, text="Refresh Rows", command=self._refresh_player_rows).grid(
            row=1, column=2, padx=8, pady=6, sticky="e"
        )
        ttk.Button(setup, text="Start Game", command=self._start_game_from_setup).grid(
            row=3, column=2, padx=8, pady=(4, 8), sticky="e"
        )
        self._refresh_player_rows()

    def _refresh_player_rows(self) -> None:
        for child in self.rows_container.winfo_children():
            child.destroy()
        count = max(3, min(6, self.player_count_var.get()))
        self.setup_name_vars = []
        self.setup_character_vars = []
        for i in range(count):
            name_var = tk.StringVar(value=f"Player {i + 1}")
            char_var = tk.StringVar(value=SUSPECTS[i])
            self.setup_name_vars.append(name_var)
            self.setup_character_vars.append(char_var)

            ttk.Label(self.rows_container, text=f"Player {i + 1} name").grid(
                row=i, column=0, padx=6, pady=4, sticky="w"
            )
            ttk.Entry(self.rows_container, textvariable=name_var, width=20).grid(
                row=i, column=1, padx=6, pady=4, sticky="ew"
            )
            ttk.Label(self.rows_container, text="Character").grid(
                row=i, column=2, padx=6, pady=4, sticky="w"
            )
            ttk.Combobox(
                self.rows_container,
                textvariable=char_var,
                values=list(SUSPECTS),
                state="readonly",
                width=18,
            ).grid(row=i, column=3, padx=6, pady=4, sticky="ew")

        self.rows_container.columnconfigure(1, weight=1)
        self.rows_container.columnconfigure(3, weight=1)

    def _start_game_from_setup(self) -> None:
        specs: List[Tuple[str, str]] = []
        seen = set()
        for name_var, char_var in zip(self.setup_name_vars, self.setup_character_vars):
            name = name_var.get().strip() or "Player"
            character = char_var.get().strip()
            if character in seen:
                messagebox.showerror("Invalid setup", "Each player must have a unique character.")
                return
            seen.add(character)
            specs.append((name, character))
        self.controller.setup_new_game(specs)
        self._build_game_screen()
        self._reveal_all_hands()
        self.refresh_view()

    def _build_game_screen(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        self.status_panel = StatusPanel(self)
        self.status_panel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4))

        self.action_panel = ActionPanel(
            self,
            on_accuse=self.on_accuse,
            on_roll=self.on_roll,
            on_move=self.on_move,
            on_suggest=self.on_suggest,
            on_end_turn=self.on_end_turn,
            on_show_hand=self.on_show_hand,
            on_export_log=self.on_export_history,
        )
        self.action_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=4)

        right = ttk.Frame(self)
        right.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(0, 10), pady=4)
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self.board_panel = BoardPanel(right)
        self.board_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        self.deduction_panel = DeductionPanel(right)
        self.deduction_panel.grid(row=1, column=0, sticky="nsew")

        self.history_panel = HistoryPanel(self)
        self.history_panel.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 10))

    def refresh_view(self) -> None:
        if not self.controller.has_game:
            return
        assert self.status_panel and self.action_panel and self.history_panel
        assert self.deduction_panel and self.board_panel

        self.status_panel.set_status(self.controller.current_status_line(), self.controller.last_roll)
        p = self.controller.current_player
        current_room = p.current_room if p else None
        self.board_panel.set_rooms(
            rooms=list(ROOMS),
            current_room=current_room,
            reachable=self.controller.reachable_map,
        )
        self.history_panel.set_lines(self.controller.public_history_lines())
        self.deduction_panel.set_text(self.controller.deduction_text_for_current())

        self.action_panel.set_enabled("accuse", self.controller.can_accuse())
        self.action_panel.set_enabled("roll", self.controller.can_roll())
        self.action_panel.set_enabled("move", self.controller.can_move())
        self.action_panel.set_enabled("suggest", self.controller.can_suggest())
        self.action_panel.set_enabled("end_turn", self.controller.can_end_turn())
        self.action_panel.set_enabled("show_hand", True)
        self.action_panel.set_enabled("export", True)

    def _reveal_all_hands(self) -> None:
        if not self.controller.engine:
            return
        for p in self.controller.engine.players:
            messagebox.showinfo(
                "Private hand reveal",
                f"{p.name} ({p.character}), pass to your seat and continue.",
                parent=self.root,
            )
            show_hand_dialog(self.root, p.name, p.character, p.hand)

    def on_accuse(self) -> None:
        if not self.controller.can_accuse():
            return
        if not messagebox.askyesno("Final accusation", "Make a final accusation (wrong means elimination)?"):
            return
        pick = choose_accusation_dialog(self.root, SUSPECTS, WEAPONS, ROOMS)
        if not pick:
            return
        outcome = self.controller.accuse(*pick)
        messagebox.showinfo("Accusation result", outcome.message)
        if outcome.status == "win":
            self.refresh_view()
            if messagebox.askyesno("Game Over", "Start a new game?"):
                self._build_setup_screen()
            return
        self.refresh_view()

    def on_roll(self) -> None:
        roll, reachable = self.controller.roll_dice()
        if not reachable:
            messagebox.showinfo(
                "Roll result",
                f"Rolled {roll}. No movement options available, staying in place.",
            )
        else:
            options = ", ".join(f"{r} ({d})" for r, d in sorted(reachable.items()))
            messagebox.showinfo("Roll result", f"Rolled {roll}. Reachable rooms: {options}")
        self.refresh_view()

    def on_move(self) -> None:
        assert self.board_panel is not None
        selected = self.board_panel.selected_room()
        if selected is None:
            if not messagebox.askyesno("Stay put", "No room selected. Stay in current room?"):
                return
        elif selected not in self.controller.reachable_map:
            messagebox.showerror("Invalid move", "Selected room is not reachable with current roll.")
            return
        msg = self.controller.move_to(selected if selected in self.controller.reachable_map else None)
        messagebox.showinfo("Movement", msg)
        if self.controller.phase == TurnPhase.ACTIONS and not self.controller.can_suggest():
            self.controller.skip_suggestion()
        self.refresh_view()

    def on_suggest(self) -> None:
        if not self.controller.can_suggest():
            return
        pick = choose_two_fields_dialog(
            parent=self.root,
            title="Make Suggestion",
            left_label="Suspect",
            left_values=SUSPECTS,
            right_label="Weapon",
            right_values=WEAPONS,
        )
        if not pick:
            return
        suspect_name, weapon_name = pick

        outcome: SuggestionOutcome = self.controller.suggest(
            suspect_name=suspect_name,
            weapon_name=weapon_name,
            choose_card=lambda responder, cards: choose_refute_card_dialog(
                self.root, responder, cards
            ),
        )
        rec = outcome.record
        summary = (
            f"{rec.suggester_name} suggested {rec.suspect} / {rec.weapon} / {rec.room}.\n"
        )
        if rec.had_refutation:
            summary += f"Refuted by {rec.refuter_name}."
        else:
            summary += "No one could refute."
        messagebox.showinfo("Suggestion", summary)
        if outcome.shown_card is not None:
            show_private_card_dialog(self.root, rec.suggester_name, outcome.shown_card)
        self.refresh_view()

    def on_end_turn(self) -> None:
        if self.controller.phase == TurnPhase.ACTIONS and self.controller.can_suggest():
            if not messagebox.askyesno("Skip suggestion", "End turn without making a suggestion?"):
                return
        self.controller.end_turn()
        self.refresh_view()

    def on_show_hand(self) -> None:
        p = self.controller.current_player
        if p is None:
            return
        messagebox.showinfo(
            "Private hand reveal",
            f"{p.name} ({p.character}), confirm others are looking away.",
        )
        show_hand_dialog(self.root, p.name, p.character, p.hand)

    def on_export_history(self) -> None:
        lines = self.controller.public_history_lines()
        if not lines:
            messagebox.showinfo("Export history", "No history entries yet.")
            return
        path = filedialog.asksaveasfilename(
            title="Export public history",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        messagebox.showinfo("Export history", f"Saved to:\n{path}")
