# 🗂️ BestSafety Services Form Manager

A modern, dark-mode file manager and secure form organizer built with Python and `ttkbootstrap`.  
Designed for efficient access, categorization, and protection of your company’s forms — including PDFs, Excel sheets, and more.

---

## 🖼️ Interface Preview

![Form Manager GUI](File%20Manager.png)

---

## ✨ Features

- 🔐 **Password Locking**  
  Easily lock and unlock access to the app. When locked:
  - Forms can't be added, opened, renamed, or deleted.
  - All interactions are disabled until the correct password is entered.

- 🔑 **Forgot Password Recovery**  
  Click **"Forgot Password?"** on the unlock dialog to reset using the master password:  
  **`mrugeshjaiswal`**

- 🧠 **Encrypted Credentials**  
  User password is hashed using **SHA-256** and stored in `settings.json`.

- 📂 **Auto Categorization**  
  All files are grouped into:
  - PDFs
  - Excel Sheets (`.xlsx`, `.xls`)
  - Other Files

- 🔍 **Search + Filter**  
  Filter files by name and file type instantly via:
  - A sidebar filter (All / PDF / Excel / Other)
  - A search bar

- 🖊️ **File Operations**  
  Double-click to open, or use toolbar buttons to rename/delete files.

- 🌙 **Modern Dark Theme**  
  Built with [`ttkbootstrap`](https://github.com/israel-dryer/ttkbootstrap) using the `darkly` theme.

- 🖼️ **Custom Icons in All Windows**  
  `appicon.ico` is embedded into every window (main + all dialogs).

- 🧷 **Portable `.exe`**  
  Fully packaged single-file `.exe` for any Windows machine — no Python needed.

---

## 📦 File Structure
Form Manager App/
├── Form Manager.py # Main application script
├── appicon.ico # Icon used for main app + dialogs
└── File Manager.png # Screenshot for documentation


---

## 🚀 How to Use

1. Launch the app (`Form Manager.py` or `.exe`)
2. Click **"Add Form"** to select a file
3. Double-click a file to open it in the default editor
4. Use **Delete**, **Rename**, and **Lock 🔒** buttons as needed
5. Default password: **`admin123`**

---

## 🔐 Changing the Password

1. Click **"🔑 Change Password"** in the sidebar
2. Enter your current password
3. Enter and confirm your new password
4. It's saved in `settings.json` as a secure SHA-256 hash

---

## 🔓 Forgot Password?

If locked out:
1. Click **"Forgot Password?"** in the unlock popup
2. Enter the **master password**:  
3. You’ll be allowed to set a new password.

---

## 🧰 Building the `.exe` (Optional)

> 🔹 Windows only — requires `pyinstaller`

1. Open terminal in the `Form Manager App` folder  
2. Run:

```
pyinstaller --noconfirm --onefile --windowed --icon=appicon.ico --add-data "appicon.ico;." "Form Manager.py"
```
This generates:

dist/
└── Form Manager.exe
