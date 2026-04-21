import tkinter as tk
from typing import Dict, Any, Optional
from tkinter import ttk, messagebox
from services.ui_helpers import make_toplevel, add_button_hover, close_current_window
from data.excel_store import (
    get_all_products, log_movement, update_inventory_summary,
    calculate_balance, SHEET_TL, wb, EXCEL_PATH
)
from config.settings import BUTTON_GREEN, ESKORT_RED, CHARCOAL_BLACK


def open_add_product_window() -> None:
    win = make_toplevel("Add New Product", "400x450")
    labels = ["Product Num", "Product Name", "Product Group",
              "Product Description", "Min Levels", "Critical Levels"]
    entries: Dict[str, Any] = {}
    for lbl in labels:
        ttk.Label(win, text=lbl).pack(pady=5)
        ent = ttk.Entry(win)
        ent.pack(pady=3, fill="x", padx=15)
        entries[lbl] = ent

    def save_product() -> None:
        if not entries["Product Name"].get():
            messagebox.showerror("Error", "Product Name is required.")
            return
        next_row = wb["Product Master"].max_row + 1
        wb["Product Master"].cell(next_row, 1).value = entries["Product Num"].get()
        wb["Product Master"].cell(next_row, 2).value = entries["Product Name"].get()
        wb["Product Master"].cell(next_row, 3).value = entries["Product Group"].get()
        wb["Product Master"].cell(next_row, 4).value = entries["Product Description"].get()
        wb["Product Master"].cell(next_row, 5).value = None
        wb["Product Master"].cell(next_row, 6).value = entries["Min Levels"].get()
        wb["Product Master"].cell(next_row, 7).value = entries["Critical Levels"].get()
        wb.save(EXCEL_PATH)
        messagebox.showinfo("Success", "Product added.")
        win.destroy()

    ttk.Button(win, text="Save Product", command=save_product).pack(pady=20)


def open_stock_in_window() -> None:
    win = make_toplevel("Stock In", "400x450")
    fields = ["Product", "Serial Number", "Make & Model",
              "Quantity", "Department", "PC Name"]
    entries: Dict[str, Any] = {}
    for f in fields:
        ttk.Label(win, text=f).pack(pady=5)
        if f == "Product":
            ent = ttk.Combobox(win, values=get_all_products())
        else:
            ent = ttk.Entry(win)
        ent.pack(pady=3, fill="x", padx=15)
        entries[f] = ent

    def save_stock_in() -> None:
        try:
            qty = int(float(entries["Quantity"].get()))
        except Exception:
            messagebox.showerror("Error", "Quantity must be an integer number.")
            return
        try:
            log_movement(
                "Stock In",
                entries["Product"].get(),
                entries["Serial Number"].get(),
                entries["Make & Model"].get(),
                qty,
                entries["Department"].get(),
                entries["PC Name"].get()
            )
            update_inventory_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record Stock-In: {e}")
            return
        messagebox.showinfo("Success", "Stock-In recorded.")
        close_current_window(win)

    ttk.Button(win, text="Save", command=save_stock_in).pack(pady=20)


def open_stock_out_window() -> None:
    win = make_toplevel("Stock Out", "400x450")
    fields = ["Product", "Serial Number", "Make & Model",
              "Quantity", "Department", "PC Name"]
    entries: Dict[str, Any] = {}
    for f in fields:
        ttk.Label(win, text=f).pack(pady=5)
        if f == "Product":
            ent = ttk.Combobox(win, values=get_all_products())
        else:
            ent = ttk.Entry(win)
        ent.pack(pady=3, fill="x", padx=15)
        entries[f] = ent

    def save_stock_out() -> None:
        try:
            qty = int(float(entries["Quantity"].get()))
        except Exception:
            messagebox.showerror("Error", "Quantity must be an integer number.")
            return
        current_balance = calculate_balance(entries["Product"].get())
        if qty > current_balance:
            messagebox.showerror("Error",
                                 f"Cannot issue {qty}. Only {current_balance} in stock.")
            return
        try:
            log_movement(
                "Stock Out",
                entries["Product"].get(),
                entries["Serial Number"].get(),
                entries["Make & Model"].get(),
                qty,
                entries["Department"].get(),
                entries["PC Name"].get()
            )
            update_inventory_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record Stock-Out: {e}")
            return
        messagebox.showinfo("Success", "Stock-Out recorded.")
        close_current_window(win)

    ttk.Button(win, text="Save", command=save_stock_out).pack(pady=20)


def open_transfer_window() -> None:
    win = make_toplevel("Transfer Product", "400x500")
    fields = ["Product", "Quantity", "From Department", "To Department", "Reason"]
    entries: Dict[str, Any] = {}
    for f in fields:
        ttk.Label(win, text=f).pack(pady=5)
        if f == "Product":
            ent = ttk.Combobox(win, values=get_all_products())
        else:
            ent = ttk.Entry(win)
        ent.pack(pady=3, fill="x", padx=15)
        entries[f] = ent

    def save_transfer() -> None:
        product = entries["Product"].get()
        try:
            qty = int(float(entries["Quantity"].get()))
        except Exception:
            messagebox.showerror("Error", "Quantity must be an integer number.")
            return
        from_dept = entries["From Department"].get()
        to_dept = entries["To Department"].get()
        reason = entries["Reason"].get()
        current_balance = calculate_balance(product)
        if qty > current_balance:
            messagebox.showerror("Error",
                                 f"Cannot transfer {qty}. Only {current_balance} available.")
            return
        try:
            log_movement("Stock Out", product, None, None, qty, from_dept, None)
            log_movement("Stock In", product, None, None, qty, to_dept, None)
            next_row = SHEET_TL.max_row + 1
            SHEET_TL.cell(next_row, 1).value = str(date.today())
            SHEET_TL.cell(next_row, 2).value = product
            SHEET_TL.cell(next_row, 3).value = from_dept
            SHEET_TL.cell(next_row, 4).value = to_dept
            SHEET_TL.cell(next_row, 5).value = qty
            SHEET_TL.cell(next_row, 6).value = reason
            wb.save(EXCEL_PATH)
            update_inventory_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record transfer: {e}")
            return
        messagebox.showinfo("Success", "Transfer recorded.")
        close_current_window(win)

    ttk.Button(win, text="Transfer", command=save_transfer).pack(pady=20)


def open_remove_product_window() -> None:
    win = make_toplevel("Remove Product (Obsolete)", "400x350")
    ttk.Label(win, text="Select Product to Remove").pack(pady=5)
    product_combo = ttk.Combobox(win, values=get_all_products())
    product_combo.pack(pady=5, fill="x", padx=15)

    def remove_product() -> None:
        product = product_combo.get()
        if not product:
            messagebox.showerror("Error", "Select a product.")
            return
        remaining_balance = calculate_balance(product)
        try:
            if remaining_balance > 0:
                log_movement("Stock Out", product, None, None,
                             remaining_balance,
                             "Obsolete", "System")
            next_row = wb["Non Stock Items"].max_row + 1
            wb["Non Stock Items"].cell(next_row, 1).value = str(date.today())
            wb["Non Stock Items"].cell(next_row, 2).value = product
            wb["Non Stock Items"].cell(next_row, 3).value = f"Removed {remaining_balance}"
            wb.save(EXCEL_PATH)
            update_inventory_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove product: {e}")
            return
        messagebox.showinfo("Success",
                            f"{product} moved to Non Stock Items and balance cleared.")
        close_current_window(win)

    ttk.Button(win, text="Remove Product", command=remove_product).pack(pady=20)
