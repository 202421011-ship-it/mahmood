import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


def open_admin_window(root):
    win = tk.Toplevel(root)
    win.title("Admin Panel")
    win.geometry("900x650")
    win.configure(bg="#f0f4f8")

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ── Tab 1: Manage Menu ────────────────────────────────────
    tab_menu = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_menu, text="  Manage Menu")

    cols = ("ID", "Name", "Category", "Price", "Available")
    tree = ttk.Treeview(tab_menu, columns=cols, show="headings", height=10)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=130)
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    def load_menu():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu_items")
        for row in cursor.fetchall():
            tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["name"],
                    row["category"],
                    f"£{row['price']:.2f}",
                    "Yes" if row["available"] else "No",
                ),
            )
        conn.close()

    load_menu()

    # Add new item form
    form = tk.LabelFrame(
        tab_menu, text="Add New Item", bg="#f0f4f8", font=("Arial", 11)
    )
    form.pack(fill="x", padx=10, pady=5)

    labels = ["Name:", "Category:", "Price:"]
    entries = {}
    for i, lbl in enumerate(labels):
        tk.Label(form, text=lbl, bg="#f0f4f8").grid(row=0, column=i * 2, padx=5, pady=5)
        e = tk.Entry(form, width=14)
        e.grid(row=0, column=i * 2 + 1, padx=5)
        entries[lbl] = e

    def add_item():
        name = entries["Name:"].get().strip()
        cat = entries["Category:"].get().strip()
        price = entries["Price:"].get().strip()
        if not all([name, cat, price]):
            messagebox.showwarning("Warning", "Please fill all fields.")
            return
        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_items (name, price, category) VALUES (?,?,?)",
            (name, price, cat),
        )
        conn.commit()
        conn.close()
        for e in entries.values():
            e.delete(0, "end")
        load_menu()
        messagebox.showinfo("Success", f"'{name}' added successfully!")

    def toggle_availability():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an item first.")
            return
        item_id = tree.item(sel[0])["values"][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE menu_items SET available = 1 - available WHERE id=?", (item_id,)
        )
        conn.commit()
        conn.close()
        load_menu()

    def delete_item():
        """Delete selected menu item (FR-18)."""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an item first.")
            return
        item_id = tree.item(sel[0])["values"][0]
        item_name = tree.item(sel[0])["values"][1]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{item_name}'?\n"
            "This cannot be undone.",
        )
        if not confirm:
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        load_menu()
        messagebox.showinfo("Deleted", f"'{item_name}' has been deleted.")

    tk.Button(
        form, text="Add", font=("Arial", 11), bg="#4CAF50", fg="white", command=add_item
    ).grid(row=0, column=6, padx=10)

    frame_btns = tk.Frame(tab_menu, bg="#f0f4f8")
    frame_btns.pack(pady=4)
    tk.Button(
        frame_btns,
        text="Toggle Available",
        font=("Arial", 11),
        bg="#FF9800",
        fg="white",
        command=toggle_availability,
    ).pack(side="left", padx=5)
    tk.Button(
        frame_btns,
        text="Delete Item",
        font=("Arial", 11),
        bg="#f44336",
        fg="white",
        command=delete_item,
    ).pack(side="left", padx=5)
    tk.Button(
        frame_btns,
        text="Refresh",
        font=("Arial", 11),
        bg="#607D8B",
        fg="white",
        command=load_menu,
    ).pack(side="left", padx=5)

    # ── Tab 2: Order Summary Report (FR-15) ───────────────────
    tab_reports = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_reports, text="  Order Summary")

    tk.Label(
        tab_reports,
        text="Order Summary Report",
        font=("Arial", 16, "bold"),
        bg="#f0f4f8",
    ).pack(pady=10)

    cols2 = ("Order ID", "Customer", "Total", "Status", "Time")
    tree2 = ttk.Treeview(tab_reports, columns=cols2, show="headings", height=12)
    for c in cols2:
        tree2.heading(c, text=c)
        tree2.column(c, width=140)
    tree2.pack(fill="both", expand=True, padx=10)

    summary_var = tk.StringVar()
    tk.Label(
        tab_reports,
        textvariable=summary_var,
        font=("Arial", 11, "bold"),
        bg="#f0f4f8",
        fg="#2196F3",
    ).pack(pady=5)

    def load_report():
        tree2.delete(*tree2.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.id, u.full_name, o.total_price,
                   o.status, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        """
        )
        rows = cursor.fetchall()
        for row in rows:
            tree2.insert(
                "", "end", values=(row[0], row[1], f"£{row[2]:.2f}", row[3], row[4])
            )
        total_revenue = sum(r[2] for r in rows)
        completed = sum(1 for r in rows if r[3] == "completed")
        queued = sum(1 for r in rows if r[3] == "queued")
        preparing = sum(1 for r in rows if r[3] == "preparing")
        ready = sum(1 for r in rows if r[3] == "ready")
        summary_var.set(
            f"Total: {len(rows)}  |  Queued: {queued}  |  Preparing: {preparing}  "
            f"|  Ready: {ready}  |  Completed: {completed}  |  Revenue: £{total_revenue:.2f}"
        )
        conn.close()

    load_report()
    tk.Button(
        tab_reports,
        text="Refresh",
        font=("Arial", 11),
        bg="#2196F3",
        fg="white",
        command=load_report,
    ).pack(pady=5)

    # ── Tab 3: Peak Hour Analysis (FR-16) ─────────────────────
    tab_peak = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_peak, text="  Peak Hours")

    tk.Label(
        tab_peak, text="Peak Hour Analysis", font=("Arial", 16, "bold"), bg="#f0f4f8"
    ).pack(pady=10)
    tk.Label(
        tab_peak,
        text="Number of orders placed per hour of the day",
        font=("Arial", 10),
        bg="#f0f4f8",
        fg="#555",
    ).pack()

    cols3 = ("Hour", "Orders", "Revenue (£)", "Busiest?")
    tree3 = ttk.Treeview(tab_peak, columns=cols3, show="headings", height=14)
    for c in cols3:
        tree3.heading(c, text=c)
        tree3.column(c, width=160)
    tree3.pack(fill="both", expand=True, padx=10, pady=5)
    tree3.tag_configure("peak", background="#fff3cd")

    def load_peak():
        tree3.delete(*tree3.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT strftime('%H:00', created_at) AS hour,
                   COUNT(*) AS order_count,
                   SUM(total_price) AS revenue
            FROM orders
            GROUP BY hour
            ORDER BY order_count DESC
        """
        )
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            tree3.insert("", "end", values=("No data", "-", "-", "-"))
            return
        max_count = rows[0][1]
        for row in rows:
            is_peak = "PEAK" if row[1] == max_count else ""
            tag = ("peak",) if row[1] == max_count else ()
            tree3.insert(
                "", "end", values=(row[0], row[1], f"{row[2]:.2f}", is_peak), tags=tag
            )

    load_peak()
    tk.Button(
        tab_peak,
        text="Refresh",
        font=("Arial", 11),
        bg="#9C27B0",
        fg="white",
        command=load_peak,
    ).pack(pady=5)

    # ── Tab 4: Popular Menu Items (FR-17) ─────────────────────
    tab_popular = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab_popular, text="  Popular Items")

    tk.Label(
        tab_popular,
        text="Most Popular Menu Items",
        font=("Arial", 16, "bold"),
        bg="#f0f4f8",
    ).pack(pady=10)
    tk.Label(
        tab_popular,
        text="Ranked by total quantity ordered",
        font=("Arial", 10),
        bg="#f0f4f8",
        fg="#555",
    ).pack()

    cols4 = (
        "Rank",
        "Item Name",
        "Category",
        "Times Ordered",
        "Units Sold",
        "Revenue (£)",
    )
    tree4 = ttk.Treeview(tab_popular, columns=cols4, show="headings", height=14)
    tree4.column("Rank", width=60)
    tree4.column("Item Name", width=160)
    tree4.column("Category", width=110)
    tree4.column("Times Ordered", width=120)
    tree4.column("Units Sold", width=100)
    tree4.column("Revenue (£)", width=110)
    for c in cols4:
        tree4.heading(c, text=c)
    tree4.pack(fill="both", expand=True, padx=10, pady=5)
    tree4.tag_configure("top", background="#d4edda")

    def load_popular():
        tree4.delete(*tree4.get_children())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.name, m.category,
                   COUNT(DISTINCT oi.order_id)  AS times_ordered,
                   SUM(oi.quantity)              AS units_sold,
                   SUM(oi.quantity * oi.unit_price) AS revenue
            FROM order_items oi
            JOIN menu_items m ON oi.menu_item_id = m.id
            GROUP BY oi.menu_item_id
            ORDER BY units_sold DESC
        """
        )
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            tree4.insert("", "end", values=("-", "No orders yet", "-", "-", "-", "-"))
            return
        for rank, row in enumerate(rows, start=1):
            tag = ("top",) if rank <= 3 else ()
            tree4.insert(
                "",
                "end",
                values=(f"#{rank}", row[0], row[1], row[2], row[3], f"{row[4]:.2f}"),
                tags=tag,
            )

    load_popular()
    tk.Button(
        tab_popular,
        text="Refresh",
        font=("Arial", 11),
        bg="#009688",
        fg="white",
        command=load_popular,
    ).pack(pady=5)
