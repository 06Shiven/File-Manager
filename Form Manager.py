import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import sys
import hashlib

FORMS_FILE = 'forms.json'
SETTINGS_FILE = 'settings.json'
DEFAULT_PASSWORD = "admin123"
MASTER_PASSWORD = "master123"


# ---------------- Password Hashing ----------------
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- Settings Handling ----------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    # First-time use: store hashed default password
    return {"password": hash_pw(DEFAULT_PASSWORD)}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)


settings = load_settings()


# ---------------- File Functions ----------------
def load_forms():
    if os.path.exists(FORMS_FILE):
        with open(FORMS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_forms(forms):
    with open(FORMS_FILE, 'w') as f:
        json.dump(forms, f, indent=4)


def add_form():
    if is_locked:
        return
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")], parent=app)
    if file_path and file_path not in forms:
        forms.append(file_path)
        save_forms(forms)
        update_grid()


def open_file(path):
    if is_locked:
        return
    if os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Error", "File not found.", parent=app)


def delete_selected():
    if is_locked or not selected_file:
        return
    if messagebox.askyesno("Delete", f"Delete '{os.path.basename(selected_file)}'?", parent=app):
        forms.remove(selected_file)
        save_forms(forms)
        update_grid()


def rename_selected():
    if is_locked or not selected_file:
        return
    new_name = ttk.simpledialog.askstring("Rename", "Enter new filename (with extension):", parent=app)
    if new_name:
        new_path = os.path.join(os.path.dirname(selected_file), new_name)
        try:
            os.rename(selected_file, new_path)
            index = forms.index(selected_file)
            forms[index] = new_path
            save_forms(forms)
            update_grid()
        except Exception as e:
            messagebox.showerror("Rename Failed", str(e), parent=app)


def set_filter(ftype):
    global current_filter
    current_filter = ftype
    update_grid()


# ---------------- Lock + Password ----------------
def toggle_lock():
    global is_locked
    if is_locked:
        unlock_dialog()
    else:
        is_locked = True
        lock_btn.config(text="🔒")
        update_grid()


def unlock_dialog():
    dlg = ttk.Toplevel(app)
    dlg.title("Unlock")
    dlg.geometry("300x150")
    dlg.transient(app)
    dlg.grab_set()
    dlg.resizable(False, False)
    dlg.iconbitmap(icon_path)

    ttk.Label(dlg, text="Enter Password:", bootstyle="inverse").pack(pady=10)
    pwd_var = tk.StringVar()
    pwd_entry = ttk.Entry(dlg, textvariable=pwd_var, show="*", bootstyle="dark")
    pwd_entry.pack(pady=5)
    pwd_entry.focus()

    def attempt_unlock():
        if hash_pw(pwd_var.get()) == settings["password"]:
            global is_locked
            is_locked = False
            lock_btn.config(text="🔓")
            update_grid()
            dlg.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.", parent=dlg)

    def forgot_password():
        dlg.destroy()
        forgot_password_dialog()

    btn_frame = ttk.Frame(dlg)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Unlock", command=attempt_unlock, bootstyle="success").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Forgot Password?", command=forgot_password, bootstyle="warning").pack(side="left",
                                                                                                      padx=5)


def forgot_password_dialog():
    dlg = ttk.Toplevel(app)
    dlg.title("Reset Password")
    dlg.geometry("300x200")
    dlg.transient(app)
    dlg.grab_set()
    dlg.resizable(False, False)
    dlg.iconbitmap(icon_path)

    ttk.Label(dlg, text="Enter Master Password:", bootstyle="inverse").pack(pady=10)
    master_var = tk.StringVar()
    master_entry = ttk.Entry(dlg, textvariable=master_var, show="*", bootstyle="dark")
    master_entry.pack(pady=5)
    master_entry.focus()

    def verify_master():
        if master_var.get() == MASTER_PASSWORD:
            dlg.destroy()
            change_password(master_override=True)
        else:
            messagebox.showerror("Error", "Incorrect master password.", parent=dlg)

    ttk.Button(dlg, text="Verify", command=verify_master, bootstyle="success").pack(pady=10)


def change_password(master_override=False):
    dlg = ttk.Toplevel(app)
    dlg.title("Change Password")
    dlg.geometry("300x250")
    dlg.transient(app)
    dlg.grab_set()
    dlg.resizable(False, False)
    dlg.iconbitmap(icon_path)

    entries = {}

    def add_field(label_text, var_name, show=""):
        ttk.Label(dlg, text=label_text, bootstyle="inverse").pack(pady=5)
        var = tk.StringVar()
        entry = ttk.Entry(dlg, textvariable=var, show=show, bootstyle="dark")
        entry.pack(pady=5)
        entries[var_name] = var

    if not master_override:
        add_field("Current Password:", "current", show="*")
    add_field("New Password:", "new", show="*")
    add_field("Confirm Password:", "confirm", show="*")

    def update_password():
        if not master_override:
            if hash_pw(entries["current"].get()) != settings["password"]:
                messagebox.showerror("Error", "Incorrect current password.", parent=dlg)
                return
        if entries["new"].get() != entries["confirm"].get():
            messagebox.showerror("Error", "Passwords do not match.", parent=dlg)
            return
        settings["password"] = hash_pw(entries["new"].get())
        save_settings(settings)
        messagebox.showinfo("Success", "Password changed successfully.", parent=dlg)
        dlg.destroy()

    ttk.Button(dlg, text="Change Password", command=update_password, bootstyle="success").pack(pady=10)


# ---------------- Grid Display ----------------
def update_grid():
    for widget in content_frame.winfo_children():
        widget.destroy()
    global selected_file
    selected_file = None

    query = search_var.get().lower().strip()
    grouped = {"PDFs": [], "Excel": [], "Other": []}

    for f in forms:
        name = os.path.basename(f)
        if query and query not in name.lower():
            continue
        if name.endswith(".pdf"):
            grouped["PDFs"].append(f)
        elif name.endswith((".xlsx", ".xls")):
            grouped["Excel"].append(f)
        else:
            grouped["Other"].append(f)

    for category, files in grouped.items():
        if current_filter != "All" and category != current_filter:
            continue
        if not files:
            continue

        label = ttk.Label(content_frame, text=category, style="h4.TLabel")
        label.pack(anchor="w", padx=5, pady=(10, 4))

        grid = ttk.Frame(content_frame)
        grid.pack(fill="x", padx=5)

        cols = 3
        for i, f in enumerate(files):
            name = os.path.basename(f)
            btn = ttk.Button(
                grid,
                text=name,
                style="primary.TButton",
                width=24,
                state="disabled" if is_locked else "normal"
            )
            btn.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="w")

            def on_double_click(event, path=f):
                global selected_file
                selected_file = path
                open_file(path)

            def on_single_click(event, path=f):
                global selected_file
                selected_file = path

            btn.bind("<Button-1>", on_single_click)
            btn.bind("<Double-1>", on_double_click)


# ---------------- INIT ----------------
forms = load_forms()
current_filter = "All"
selected_file = None
is_locked = False

app = ttk.Window(themename="darkly")
app.title("Form Manager")

try:
    if getattr(sys, 'frozen', False):
        icon_path = os.path.join(sys._MEIPASS, 'appicon.ico')
    else:
        icon_path = 'appicon.ico'
    app.iconbitmap(icon_path)
except Exception as e:
    print("Icon load failed:", e)

app.geometry("900x600")

# Sidebar
sidebar = ttk.Frame(app, padding=10)
sidebar.pack(side="left", fill="y")

ttk.Label(sidebar, text="Actions", style="h5.TLabel").pack(pady=(10, 5), anchor="w")
ttk.Button(sidebar, text="Add Form", bootstyle="info-outline", command=add_form).pack(fill="x", pady=4)
ttk.Button(sidebar, text="🔑 Change Password", bootstyle="warning-outline", command=change_password).pack(fill="x",
                                                                                                         pady=(15, 6))

ttk.Label(sidebar, text="Filter", style="h5.TLabel").pack(pady=(20, 5), anchor="w")
for name in ["All", "PDFs", "Excel", "Other"]:
    ttk.Button(sidebar, text=name, bootstyle="secondary-outline", command=lambda f=name: set_filter(f)).pack(fill="x",
                                                                                                             pady=3)

# Main Frame
main_frame = ttk.Frame(app, padding=10)
main_frame.pack(side="right", fill="both", expand=True)

ttk.Label(main_frame, text="Form Manager", style="h2.TLabel").pack(pady=(0, 10))

# Search + Lock Area
search_action_frame = ttk.Frame(main_frame)
search_action_frame.pack(fill="x")

search_var = tk.StringVar()
search_entry = ttk.Entry(search_action_frame, textvariable=search_var)
search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

ttk.Button(search_action_frame, text="Delete", bootstyle="danger-outline", command=delete_selected).pack(side="right", padx=(5, 0))
ttk.Button(search_action_frame, text="Rename", bootstyle="warning-outline", command=rename_selected).pack(side="right")

lock_btn = tk.Button(
    search_action_frame,
    text="🔓",
    font=("Segoe UI Emoji", 14),
    width=3,
    command=toggle_lock,
    bg="#2a2d2e",
    fg="white",
    bd=0,
    activebackground="#444444"
)
lock_btn.pack(side="right", padx=(10, 5))

# Scrollable Content Area
canvas = tk.Canvas(main_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scroll_frame = ttk.Frame(canvas)

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True, pady=10)
scrollbar.pack(side="right", fill="y")

content_frame = scroll_frame

# Search behavior
search_var.trace("w", lambda *args: update_grid())
update_grid()

app.mainloop()

