"""
Animation and Transition Helpers for Contact Manager Pro.
Includes rolling counter tallying on dashboard KPIs, smooth view transitions, and button hover highlights.
"""
import tkinter as tk
from typing import Callable, Optional

def animate_counter(
    label: tk.Widget,
    target_value: int,
    duration_ms: int = 500,
    steps: int = 20,
    prefix: str = "",
    suffix: str = "",
    formatter: Optional[Callable[[int], str]] = None
) -> None:
    """
    Smoothly count up numbers on dashboard KPI cards.
    """
    if target_value <= 0:
        val_str = formatter(0) if formatter else "0"
        label.configure(text=f"{prefix}{val_str}{suffix}")
        return

    interval = max(15, duration_ms // steps)
    step_val = max(1, target_value // steps)
    current_val = [0]

    def _update():
        current_val[0] += step_val
        if current_val[0] >= target_value:
            final_str = formatter(target_value) if formatter else str(target_value)
            label.configure(text=f"{prefix}{final_str}{suffix}")
        else:
            inter_str = formatter(current_val[0]) if formatter else str(current_val[0])
            label.configure(text=f"{prefix}{inter_str}{suffix}")
            label.after(interval, _update)

    label.after(10, _update)


def add_hover_effect(widget: tk.Widget, hover_bg: str, normal_bg: str, hover_fg: str = None, normal_fg: str = None) -> None:
    """Add smooth mouseenter and mouseleave background color transitions."""
    def on_enter(e):
        try:
            widget.configure(bg=hover_bg)
            if hover_fg:
                widget.configure(fg=hover_fg)
        except Exception:
            pass

    def on_leave(e):
        try:
            widget.configure(bg=normal_bg)
            if normal_fg:
                widget.configure(fg=normal_fg)
        except Exception:
            pass

    widget.bind("<Enter>", on_enter, add="+")
    widget.bind("<Leave>", on_leave, add="+")
