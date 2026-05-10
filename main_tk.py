#!/usr/bin/env python3
"""Tkinter entrypoint for Cluedo hot-seat UI."""

from __future__ import annotations

import argparse
import tkinter as tk
from typing import List, Optional

from ui.app import CluedoApp


def run_ui(seed: Optional[int], log_path: Optional[str]) -> int:
    root = tk.Tk()
    root.title("Cluedo / Clue - Hot-seat UI")
    root.geometry("1200x760")
    CluedoApp(root=root, seed=seed, log_path=log_path)
    root.mainloop()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Cluedo / Clue Tkinter UI")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible deals")
    parser.add_argument(
        "--log",
        metavar="FILE",
        default=None,
        help="Append suggestion/refutation session logs to this file",
    )
    args = parser.parse_args(argv)
    return run_ui(seed=args.seed, log_path=args.log)


if __name__ == "__main__":
    raise SystemExit(main())
