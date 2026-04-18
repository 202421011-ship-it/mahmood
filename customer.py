import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from auth import get_current_user

def open_customer_window(root):
    user = get_current_user()
    win = tk.Toplevel(root)
    win.title(f"Customer Panel - {user['full_name']}")
    win.geometry("800x600")
    win.configure(bg="#f0f4f8")

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ── تاب المنيو ──────────────────────────────────────────
    tab_menu = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_menu, text="🍔 Menu")

    tk.Label(tab_menu, text="Browse Menu", font=("Arial", 16, "bold"),
             bg="#f0f4f8").pack(pady=10)

    cart = {}  # item_id -> {name, price, qty}

    frame_top = tk.Frame(tab_menu, bg="#f0f4f8")
    frame_top.pack(fill="both", expand=True, padx=10)

    cols = ("Item", "Category", "Price", "")
    tree = ttk.Treeview(frame_top, columns=cols, show="headings", height=12)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=150)
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame_top, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")

    def load_menu():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu_items WHERE available=1")
        for row in cursor.fetchall():
            tree.insert("", "end", iid=row["id"],
                        values=(row["name"], row["category"],
                                f"£{row['price']:.2f}", "Add to cart"))
        conn.close()

    load_menu()

    def add_to_cart():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        item_id = int(sel[0])
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu_items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        conn.close()
        if item_id in cart:
            cart[item_id]["qty"] += 1
        else:
            cart[item_id] = {"name": item["name"],
                             "price": item["price"], "qty": 1}
        update_cart_display()

    tk.Button(tab_menu, text="➕ Add to Cart", font=("Arial", 12),
              bg="#4CAF50", fg="white", command=add_to_cart).pack(pady=5)

    # Cart display
    tk.Label(tab_menu, text="Your Cart:", font=("Arial", 12, "bold"),
             bg="#f0f4f8").pack()
    cart_var = tk.StringVar(value="Cart is empty")
    tk.Label(tab_menu, textvariable=cart_var, bg="#f0f4f8",
             font=("Arial", 10), justify="left").pack()

    total_var = tk.StringVar(value="Total: £0.00")
    tk.Label(tab_menu, textvariable=total_var, font=("Arial", 12, "bold"),
             bg="#f0f4f8", fg="#e74c3c").pack()

    def update_cart_display():
        if not cart:
            cart_var.set("Cart is empty")
            total_var.set("Total: £0.00")
            return
        lines = [f"  {v['name']} x{v['qty']}  £{v['price']*v['qty']:.2f}"
                 for v in cart.values()]
        cart_var.set("\n".join(lines))
        total = sum(v["price"] * v["qty"] for v in cart.values())
        total_var.set(f"Total: £{total:.2f}")

    def clear_cart():
        cart.clear()
        update_cart_display()

    def place_order():
        if not cart:
            messagebox.showwarning("Warning", "Your cart is empty!")
            return
        user = get_current_user()
        total = sum(v["price"] * v["qty"] for v in cart.values())
        conn = get_connection()
        cursor = conn.cursor()

        # حساب queue position
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE status IN ('queued','preparing')"
        )
        queue_pos = cursor.fetchone()[0] + 1

        cursor.execute(
            "INSERT INTO orders (user_id, total_price, status, queue_position) VALUES (?,?,?,?)",
            (user["id"], total, "queued", queue_pos)
        )
        order_id = cursor.lastrowid
        for item_id, v in cart.items():
            cursor.execute(
                "INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price) VALUES (?,?,?,?)",
                (order_id, item_id, v["qty"], v["price"])
            )
        conn.commit()
        conn.close()
        cart.clear()
        update_cart_display()
        messagebox.showinfo("Order Placed",
                            f"✅ Order placed!\nQueue position: #{queue_pos}")
        load_orders()

    frame_btns = tk.Frame(tab_menu, bg="#f0f4f8")
    frame_btns.pack(pady=5)
    tk.Button(frame_btns, text="🛒 Place Order", font=("Arial", 12),
              bg="#2196F3", fg="white", command=place_order).pack(side="left", padx=5)
    tk.Button(frame_btns, text="🗑 Clear Cart", font=("Arial", 12),
              bg="#f44336", fg="white", command=clear_cart).pack(side="left", padx=5)

    # ── تاب الطلبات ──────────────────────────────────────────
    tab_orders = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_orders, text="📋 My Orders")

    tk.Label(tab_orders, text="My Order History",
             font=("Arial", 16, "bold"), bg="#f0f4f8").pack(pady=10)

    cols2 = ("Order ID", "Total", "Status", "Queue #", "Time")
    tree2 = ttk.Treeview(tab_orders, columns=cols2, show="headings", height=15)
    for c in cols2:
        tree2.heading(c, text=c)
        tree2.column(c, width=130)
    tree2.pack(fill="both", expand=True, padx=10)

    # Color tags for status
    tree2.tag_configure("queued",    background="#fff9c4")
    tree2.tag_configure("preparing", background="#ffe0b2")
    tree2.tag_configure("ready",     background="#c8e6c9")
    tree2.tag_configure("completed", background="#e0e0e0")

    def load_orders():
        tree2.delete(*tree2.get_children())
        user = get_current_user()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
            (user["id"],)
        )
        for row in cursor.fetchall():
            tree2.insert("", "end",
                         values=(row["id"], f"£{row['total_price']:.2f}",
                                 row["status"], f"#{row['queue_position']}",
                                 row["created_at"]),
                         tags=(row["status"],))
        conn.close()

    load_orders()
    tk.Button(tab_orders, text="🔄 Refresh", font=("Arial", 11),
              bg="#607D8B", fg="white",
              command=load_orders).pack(pady=5)