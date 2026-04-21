import tkinter as tk
from services.ui_helpers import setup_ui_styles, add_button_hover, push_window
from ui.dashboard import open_dashboard
from ui.dialogs.product_windows import open_stock_in_window, open_stock_out_window
from config.settings import ESKORT_BLUE, ESKORT_RED, WHITE


def main_app() -> None:
    global root
    root = tk.Tk()
    setup_ui_styles()
    root.title("IT Inventory System")
    root.geometry("600x500")
    root.configure(bg=WHITE)
    push_window(root)

    tk.Label(root, text="IT Inventory System", font=("Segoe UI", 18, "bold"), bg=WHITE).pack(pady=30)

    btn_open = tk.Button(root, text="Open Dashboard", font=("Segoe UI", 14, "bold"), bg=ESKORT_BLUE, fg=WHITE, command=open_dashboard)
    btn_open.pack(fill="x", padx=40, pady=20)
    add_button_hover(btn_open, ESKORT_BLUE)

    btn_in = tk.Button(root, text="Stock In", font=("Segoe UI", 14, "bold"), bg=ESKORT_BLUE, fg=WHITE, command=open_stock_in_window)
    btn_in.pack(fill="x", padx=40, pady=10)
    add_button_hover(btn_in, ESKORT_BLUE)

    btn_out = tk.Button(root, text="Stock Out", font=("Segoe UI", 14, "bold"), bg=ESKORT_BLUE, fg=WHITE, command=open_stock_out_window)
    btn_out.pack(fill="x", padx=40, pady=10)
    add_button_hover(btn_out, ESKORT_BLUE)

    btn_exit = tk.Button(root, text="Exit", font=("Segoe UI", 12), bg=ESKORT_RED, fg=WHITE, command=root.quit)
    btn_exit.pack(fill="x", padx=40, pady=10)
    add_button_hover(btn_exit, ESKORT_RED)

    root.mainloop()


if __name__ == "__main__":
    main_app()
