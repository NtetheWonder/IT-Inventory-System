import tkinter as tk
from tkinter import ttk
from typing import Tuple, Optional
from config.settings import ESKORT_BLUE, WHITE

# Small color helper
def _adjust_hex_brightness(hex_color: str, factor: float = 0.9) -> str:
    """Lighten or darken a hex color string by factor."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return hex_color
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except Exception:
        return '#'+hex_color
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"


def add_button_hover(btn, base_color):
    try:
        hover = _adjust_hex_brightness(base_color, 0.88)
        def on_enter(e):
            try:
                btn['background'] = hover
            except Exception:
                pass
        def on_leave(e):
            try:
                btn['background'] = base_color
            except Exception:
                pass
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
    except Exception:
        pass


def setup_ui_styles():
    try:
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        default_font = ('Segoe UI', 11)
        style.configure('.', font=default_font)
        style.configure('Treeview.Heading', background=ESKORT_BLUE, foreground=WHITE,
                        font=('Segoe UI', 10, 'bold'))
        style.configure('Treeview', rowheight=24, font=default_font)
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=6)
    except Exception:
        pass


# Status computation
def compute_status(balance: int | str | float, min_level: Optional[int] | str | float, critical_level: Optional[int] | str | float) -> str:
    """Compute inventory status using integer thresholds.

    Coerce values to integers where possible; missing thresholds are ignored.
    """
    try:
        balance_int = int(float(balance))
    except Exception:
        balance_int = 0

    try:
        crit = int(float(critical_level))
    except Exception:
        crit = None

    try:
        minl = int(float(min_level))
    except Exception:
        minl = None

    if crit is not None and balance_int <= crit:
        return 'CRITICAL'
    if minl is not None and balance_int <= minl:
        return 'LOW'
    return 'OK'


# Table sorting functionality
def setup_treeview_sorting(treeview: ttk.Treeview, numeric_columns: list = None, status_column: str | None = None):
    """Enable robust sorting by clicking on column headers.

    This stores sorting state on the treeview so it can be reapplied
    after the widget's contents are repopulated (useful when data is
    refreshed on a timer).

    Args:
        treeview: The ttk.Treeview widget to enable sorting on
        numeric_columns: List of column names that should be sorted numerically
        status_column: Column name containing status values (CRITICAL/LOW/OK)
    """
    if numeric_columns is None:
        numeric_columns = []

    # Attach a persistent sort state to the widget
    treeview._sort_state = {
        'column': None,
        'reverse': False,
        'numeric_columns': set(numeric_columns),
        'status_column': status_column,
    }

    def _to_number(s: str):
        try:
            return float(s)
        except Exception:
            return float('inf') if s == '' else 0.0

    def sort_by(col: str, reverse: bool | None = None):
        """Sort table by the given column and update stored state.

        If `reverse` is None, the ordering toggles when the same column
        is clicked; otherwise it forces the given direction.
        """
        ss = treeview._sort_state
        if reverse is None:
            if ss['column'] == col:
                ss['reverse'] = not ss['reverse']
            else:
                ss['column'] = col
                ss['reverse'] = False
        else:
            ss['column'] = col
            ss['reverse'] = bool(reverse)

        reverse_flag = ss['reverse']

        items = [(treeview.set(k, col), k) for k in treeview.get_children('')]

        # Custom ordering for status column
        if ss.get('status_column') and col == ss['status_column']:
            order = {'CRITICAL': 0, 'LOW': 1, 'OK': 2}
            items.sort(key=lambda x: (order.get(x[0].upper(), 3), treeview.set(x[1], ss.get('column', '') or '').lower()), reverse=reverse_flag)
        elif col in ss['numeric_columns']:
            items.sort(key=lambda x: (_to_number(x[0]), treeview.set(x[1], ss.get('column', '') or '').lower()), reverse=reverse_flag)
        else:
            items.sort(key=lambda x: (x[0].lower() if isinstance(x[0], str) else str(x[0]).lower(),), reverse=reverse_flag)

        for index, (_, k) in enumerate(items):
            treeview.move(k, '', index)

    # Expose the sorter and a reapply helper on the widget so callers can
    # reapply the last sort after a data refresh.
    treeview.sort_by = sort_by

    def reapply_sort():
        ss = getattr(treeview, '_sort_state', None)
        if not ss:
            return
        col = ss.get('column')
        if col:
            # Force the same direction that's stored
            sort_by(col, reverse=ss.get('reverse', False))

    treeview.reapply_sort = reapply_sort

    for col in treeview['columns']:
        treeview.heading(col, command=lambda c=col: sort_by(c))


# Window history management
window_history = []

def push_window(win):
    global window_history
    if window_history:
        try:
            window_history[-1].withdraw()
        except Exception:
            pass
    window_history.append(win)
    try:
        win.focus_force()
    except Exception:
        pass


def close_current_window(win):
    global window_history
    try:
        if window_history and window_history[-1] is win:
            window_history.pop()
        try:
            win.destroy()
        except Exception:
            pass
        if window_history:
            try:
                prev = window_history[-1]
                prev.deiconify()
                prev.focus_force()
            except Exception:
                pass
        else:
            try:
                if 'root' in globals() and isinstance(root, tk.Tk):
                    root.quit()
            except Exception:
                pass
    except Exception:
        try:
            win.destroy()
        except Exception:
            pass


def make_toplevel(title, geometry=None):
    win = tk.Toplevel()
    win.title(title)
    if geometry:
        try:
            win.geometry(geometry)
        except Exception:
            pass
    top_frame = tk.Frame(win)
    top_frame.pack(fill='x')
    back_btn = tk.Button(top_frame, text='Back', command=lambda w=win: close_current_window(w))
    back_btn.pack(side='left', padx=6, pady=4)
    win.protocol('WM_DELETE_WINDOW', lambda w=win: close_current_window(w))
    push_window(win)
    return win
