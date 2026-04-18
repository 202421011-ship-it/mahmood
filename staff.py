import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

def open_staff_window(root):
    win = tk.Toplevel(root)
    win.title("Staff Panel - Order Management")
    win.geometry("750x500")
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Active Orders Queue", font=("Arial", 16, "bold"),
             bg="#f0f4f8").pack(pady=10)

    cols = ("Order ID", "Customer", "Total", "Status", "Queue #", "Time")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=14)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=110)
    tree.pack(fill="both", expand=True, padx=10)

    tree.tag_configure("queued",    background="#fff9c4")
    tree.tag_configure("preparing", background="#ffe0b2")
    tree.tag_configure("ready",     background="#c8e6c9")
    tree.tag_configure("completed", background="#e0e0e0")

    def load_orders():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, u.full_name, o.total_price,
                   o.status, o.queue_position, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.status != 'completed'
            ORDER BY o.queue_position ASC
        """)
        for row in cursor.fetchall():
            tree.insert("", "end",
                        values=(row[0], row[1], f"£{row[2]:.2f}",
                                row[3], f"#{row[4]}", row[5]),
                        tags=(row[3],))
        conn.close()

    load_orders()

    def update_status(new_status):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an order first")
            return
        order_id = tree.item(sel[0])["values"][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (new_status, order_id)
        )
        conn.commit()
        conn.close()
        load_orders()
        messagebox.showinfo("Updated", f"Order #{order_id} → {new_status}")

    frame_btns = tk.Frame(win, bg="#f0f4f8")
    frame_btns.pack(pady=8)

    statuses = [
        ("⏳ Queued",    "queued",    "#9E9E9E"),
        ("🔥 Preparing", "preparing", "#FF9800"),
        ("✅ Ready",     "ready",     "#4CAF50"),
        ("☑ Completed", "completed", "#607D8B"),
    ]
    for label, status, color in statuses:
        tk.Button(frame_btns, text=label, font=("Arial", 11),
                  bg=color, fg="white",
                  command=lambda s=status: update_status(s)
                  ).pack(side="left", padx=4)

    tk.Button(win, text="🔄 Refresh", font=("Arial", 11),
              bg="#2196F3", fg="white",
              command=load_orders).pack(pady=5)