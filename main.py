import tkinter as tk
from tkinter import messagebox
from database import init_db
from auth import login, logout
import customer, staff, admin

def main():
    init_db()

    root = tk.Tk()
    root.title("Smart Food Ordering & Queue Management System")
    root.geometry("420x480")
    root.configure(bg="#1a1a2e")
    root.resizable(False, False)

    # ── Header ───────────────────────────────────────────────
    tk.Label(root, text="🍽️ SFOQS", font=("Arial", 28, "bold"),
             bg="#1a1a2e", fg="#e94560").pack(pady=20)
    tk.Label(root, text="Smart Food Ordering System",
             font=("Arial", 12), bg="#1a1a2e", fg="#a8a8b3").pack()

    # ── Login Frame ───────────────────────────────────────────
    frame = tk.Frame(root, bg="#16213e", padx=30, pady=30)
    frame.pack(pady=30, padx=40, fill="x")

    tk.Label(frame, text="Username", font=("Arial", 11),
             bg="#16213e", fg="white").pack(anchor="w")
    entry_user = tk.Entry(frame, font=("Arial", 12), width=28)
    entry_user.pack(pady=5)

    tk.Label(frame, text="Password", font=("Arial", 11),
             bg="#16213e", fg="white").pack(anchor="w", pady=(10, 0))
    entry_pass = tk.Entry(frame, font=("Arial", 12),
                          width=28, show="*")
    entry_pass.pack(pady=5)

    status_var = tk.StringVar()
    tk.Label(frame, textvariable=status_var, font=("Arial", 10),
             bg="#16213e", fg="#e94560").pack(pady=5)

    def do_login():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not username or not password:
            status_var.set("⚠ Please enter username and password")
            return
        if login(username, password):
            from auth import get_current_user
            user = get_current_user()
            role = user["role"]
            if role == "customer":
                customer.open_customer_window(root)
            elif role == "staff":
                staff.open_staff_window(root)
            elif role == "admin":
                admin.open_admin_window(root)
            entry_user.delete(0, "end")
            entry_pass.delete(0, "end")
            status_var.set("")
        else:
            status_var.set("❌ Wrong username or password")

    entry_pass.bind("<Return>", lambda e: do_login())

    tk.Button(frame, text="Login", font=("Arial", 13, "bold"),
              bg="#e94560", fg="white", width=20,
              command=do_login).pack(pady=10)

    # ── Hint ──────────────────────────────────────────────────
    hint = (
        "admin / admin123\n"
        "staff1 / staff123\n"
        "customer1 / customer123"
    )
    tk.Label(root, text=hint, font=("Arial", 9),
             bg="#1a1a2e", fg="#555577").pack()

    root.mainloop()

if __name__ == "__main__":
    main()