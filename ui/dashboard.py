import tkinter as tk
from typing import Any, Dict, List
from tkinter import ttk
from services.ui_helpers import make_toplevel, add_button_hover, setup_ui_styles
from services.ui_helpers import compute_status, setup_treeview_sorting
from data.excel_store import (
    calculate_all_balances,
    get_total_stock_in_out,
    get_all_products,
    get_all_product_groups,
    count_obsolete,
    get_min_critical,
    get_product_group_map,
    get_product_group,
)
from config.settings import (
    WHITE, SIDEBAR_GREY, ESKORT_BLUE, BUTTON_GREEN, ESKORT_RED,
    CHARCOAL_BLACK, CRIT_BG, LOW_BG, OK_BG
)
from ui.dialogs.product_windows import (
    open_stock_in_window, open_stock_out_window, open_remove_product_window
)


def get_stock_on_hand_table() -> List[Dict[str, Any]]:
    # Delegate to data layer if needed; kept for compatibility
    from data.excel_store import get_stock_on_hand_table
    return get_stock_on_hand_table()


def open_dashboard() -> None:
    dash = make_toplevel("IT Inventory Dashboard", "1450x850")
    dash.configure(bg=WHITE)
    sidebar = tk.Frame(dash, width=260, bg=SIDEBAR_GREY)
    sidebar.pack(side="left", fill="y")
    # Prevent the sidebar frame from resizing to its children so
    # selecting items doesn't change the overall layout width/height.
    try:
        sidebar.pack_propagate(False)
    except Exception:
        pass
    tk.Label(sidebar, text="ESKORT", fg=ESKORT_RED,
             font=("Segoe UI", 16, "bold"), bg=SIDEBAR_GREY).pack(pady=18)
    tk.Label(sidebar, text="Product Type", font=("Segoe UI", 12, "bold"), bg=SIDEBAR_GREY).pack(pady=5)
    type_list = tk.Listbox(sidebar, height=6, bg=WHITE, activestyle='none', selectmode='multiple', exportselection=False)
    type_list.pack(fill="x", padx=10)
    for g in get_all_product_groups():
        type_list.insert(tk.END, g)
    # selection/filter state
    filter_groups: set[str] = set()
    filter_products: set[str] = set()
    # build product->group map once
    product_group_map = get_product_group_map()
    # cache full product list
    all_products = get_all_products()
    tk.Label(sidebar, text="Product Name", font=("Segoe UI", 12, "bold"), bg=SIDEBAR_GREY).pack(pady=5)
    product_list = tk.Listbox(sidebar, height=10, bg=WHITE, activestyle='none', exportselection=False)
    product_list.pack(fill="x", padx=10)

    def rebuild_product_list():
        """Populate `product_list` with products matching current `filter_groups`.

        If no groups are selected, show all products.
        """
        try:
            product_list.delete(0, tk.END)
        except Exception:
            pass
        for p in all_products:
            try:
                grp = product_group_map.get(p) or get_product_group(p)
            except Exception:
                grp = None
            if not filter_groups or (grp in filter_groups):
                try:
                    product_list.insert(tk.END, p)
                except Exception:
                    pass
        # restore any product-specific selection
        if filter_products:
            for i in range(product_list.size()):
                try:
                    if product_list.get(i) in filter_products:
                        product_list.selection_set(i)
                except Exception:
                    pass

    rebuild_product_list()

    

    def on_type_select(evt):
        nonlocal filter_groups, filter_products
        sel = type_list.curselection()
        # Build set of selected groups
        new_groups = set()
        for i in sel:
            try:
                new_groups.add(type_list.get(i))
            except Exception:
                pass
        filter_groups = new_groups
        # clear any product-specific filters when grouping selection changes
        filter_products.clear()
        # refresh product list to show only matching products
        rebuild_product_list()
        refresh_dashboard()

    def on_product_select(evt):
        nonlocal filter_groups, filter_products
        sel = product_list.curselection()
        if not sel:
            return
        idx = sel[0]
        try:
            prod = product_list.get(idx)
        except Exception:
            prod = None
        if not prod:
            return
        # Toggle the product's group selection if group exists, else toggle product filter
        grp = product_group_map.get(prod) or get_product_group(prod)
        if grp is not None:
            # Toggle group in selection
            if grp in filter_groups:
                filter_groups.remove(grp)
            else:
                filter_groups.add(grp)
            # Update listbox visual selection to match filter_groups
            try:
                type_list.selection_clear(0, tk.END)
                for i in range(type_list.size()):
                    try:
                        if type_list.get(i) in filter_groups:
                            type_list.selection_set(i)
                    except Exception:
                        pass
            except Exception:
                pass
            # clear product-specific filters
            filter_products.clear()
            rebuild_product_list()
        else:
            # product has no group: toggle product-specific filter
            if prod in filter_products:
                filter_products.remove(prod)
            else:
                filter_products.add(prod)
        refresh_dashboard()

    type_list.bind('<<ListboxSelect>>', on_type_select)
    product_list.bind('<<ListboxSelect>>', on_product_select)

    # (Show All button and filter indicator removed per user request)
    b_stock_in = tk.Button(sidebar, text="Stock In", command=open_stock_in_window,
              bg=BUTTON_GREEN, fg=WHITE, font=("Segoe UI", 11, "bold"))
    b_stock_in.pack(fill="x", padx=10, pady=6)
    add_button_hover(b_stock_in, BUTTON_GREEN)
    b_stock_out = tk.Button(sidebar, text="Stock Out", command=open_stock_out_window,
              bg=ESKORT_RED, fg=WHITE, font=("Segoe UI", 11, "bold"))
    b_stock_out.pack(fill="x", padx=10, pady=6)
    add_button_hover(b_stock_out, ESKORT_RED)
    b_remove = tk.Button(sidebar, text="Remove Product", command=open_remove_product_window,
              bg=CHARCOAL_BLACK, fg=WHITE, font=("Segoe UI", 11, "bold"))
    b_remove.pack(fill="x", padx=10, pady=6)
    add_button_hover(b_remove, CHARCOAL_BLACK)

    header_frame = tk.Frame(dash, bg=ESKORT_BLUE)
    header_frame.pack(fill="x")
    header = tk.Label(
        header_frame,
        text="INVENTORY MANAGEMENT SYSTEM",
        font=("Segoe UI", 22, "bold"),
        bg=ESKORT_BLUE,
        fg=WHITE,
        pady=12
    )
    header.pack()

    cards_frame = tk.Frame(dash, bg=WHITE)
    cards_frame.pack(pady=15, padx=20)

    def info_card(parent, title, color):
        frame = tk.Frame(parent, bg=color, width=220, height=90, relief='raised', bd=1)
        frame.pack(side="left", padx=12)
        frame.pack_propagate(False)
        label_title = tk.Label(frame, text=title, bg=color, fg=WHITE,
                               font=("Segoe UI", 10, "bold"))
        label_title.pack(anchor='nw', padx=10, pady=(8,0))
        label_value = tk.Label(frame, text="0", bg=color, fg=WHITE,
                               font=("Segoe UI", 20, "bold"))
        label_value.pack(anchor='sw', padx=10, pady=(0,8))
        return label_value

    card_balance   = info_card(cards_frame, "BALANCE IN STOCK", ESKORT_BLUE)
    card_stock_in  = info_card(cards_frame, "STOCK IN", BUTTON_GREEN)
    card_stock_out = info_card(cards_frame, "STOCK OUT", ESKORT_RED)
    card_obs       = info_card(cards_frame, "OBSOLETE", CHARCOAL_BLACK)

    tk.Label(dash, text="Low & Critical Items", font=("Segoe UI", 14, "bold"), bg=WHITE).pack(pady=(10, 5))
    table_frame_crit = tk.Frame(dash)
    table_frame_crit.pack(pady=5)
    columns = ("Product", "Balance", "Min", "Critical", "Status")
    table_crit = ttk.Treeview(table_frame_crit, columns=columns, show="headings", height=8)
    for col in columns:
        # Align headings consistently
        if col == 'Product':
            table_crit.heading(col, text=col, anchor='w')
            table_crit.column(col, width=320, anchor='w', stretch=False)
        elif col in ('Balance', 'Min', 'Critical'):
            table_crit.heading(col, text=col, anchor='e')
            table_crit.column(col, width=120, anchor='e', stretch=False)
        else:
            table_crit.heading(col, text=col, anchor='center')
            table_crit.column(col, width=120, anchor='center', stretch=False)
    table_crit.pack()
    setup_treeview_sorting(table_crit, numeric_columns=["Balance", "Min", "Critical"], status_column="Status")
    try:
        table_crit.tag_configure('CRITICAL', background=CRIT_BG, foreground=ESKORT_RED)
        table_crit.tag_configure('LOW', background=LOW_BG, foreground=CHARCOAL_BLACK)
        table_crit.tag_configure('OK', background=OK_BG, foreground=ESKORT_BLUE)
    except Exception:
        pass

    tk.Label(dash, text="All Stock Items", font=("Segoe UI", 14, "bold"), bg=WHITE).pack(pady=(20, 5))
    table_frame_all = tk.Frame(dash)
    table_frame_all.pack(fill="both", expand=True)
    columns_all = ("Product", "Balance", "Status")
    table_all = ttk.Treeview(table_frame_all, columns=columns_all, show="headings", height=18)
    for col in columns_all:
        if col == 'Product':
            table_all.heading(col, text=col, anchor='w')
            table_all.column(col, width=420, anchor='w', stretch=True)
        elif col == 'Balance':
            table_all.heading(col, text=col, anchor='e')
            table_all.column(col, width=120, anchor='e', stretch=False)
        else:
            table_all.heading(col, text=col, anchor='center')
            table_all.column(col, width=120, anchor='center', stretch=False)
    table_all.pack(fill="both", expand=True)
    setup_treeview_sorting(table_all, numeric_columns=["Balance"], status_column="Status")
    try:
        table_all.tag_configure('CRITICAL', background=CRIT_BG, foreground=ESKORT_RED)
        table_all.tag_configure('LOW', background=LOW_BG, foreground=CHARCOAL_BLACK)
        table_all.tag_configure('OK', background=OK_BG, foreground=ESKORT_BLUE)
    except Exception:
        pass

    def refresh_dashboard():
        table_crit.delete(*table_crit.get_children())
        table_all.delete(*table_all.get_children())
        balances = calculate_all_balances()
        total_in, total_out = get_total_stock_in_out()
        total_balance = 0
        for product, data in balances.items():
            qty_in = int(data.get("in", 0))
            qty_out = int(data.get("out", 0))
            balance = int(data.get("balance", 0))
            try:
                total_balance += balance
            except Exception:
                pass
            try:
                min_level, crit_level = get_min_critical(product)
            except Exception:
                min_level, crit_level = (None, None)
            status = compute_status(balance, min_level, crit_level)

            # Apply filtering: group set or product-specific filters
            if filter_products and product not in filter_products:
                continue
            if filter_groups:
                pg = product_group_map.get(product) or get_product_group(product)
                if pg not in filter_groups:
                    continue

            balance_display = str(int(balance))
            table_all.insert("", "end", values=(product, balance_display, status), tags=(status,))

            if status in ("LOW", "CRITICAL"):
                min_display = "" if min_level is None else str(int(min_level))
                crit_display = "" if crit_level is None else str(int(crit_level))
                table_crit.insert("", "end", values=(product, balance_display, min_display, crit_display, status), tags=(status,))
        try:
            card_balance.config(text=str(int(total_balance)))
        except Exception:
            card_balance.config(text=str(total_balance))
        card_stock_in.config(text=str(int(total_in)))
        card_stock_out.config(text=str(int(total_out)))
        card_obs.config(text=str(count_obsolete()))

        # Reapply any active sort so refresh doesn't reset ordering
        try:
            if hasattr(table_crit, 'reapply_sort'):
                table_crit.reapply_sort()
        except Exception:
            pass
        try:
            if hasattr(table_all, 'reapply_sort'):
                table_all.reapply_sort()
        except Exception:
            pass
        dash.after(3000, refresh_dashboard)

    refresh_dashboard()
