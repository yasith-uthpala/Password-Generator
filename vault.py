"""
vault.py - Password CRUD: add, view, search, edit, delete.

Improvements applied:
  ✅ secrets module for cryptographically secure generation
  ✅ SQLite storage (via storage.py)
  ✅ Full encryption (site + username + password all encrypted)
  ✅ Clipboard copy + auto-clear after 30 seconds
  ✅ Password strength checker + forced character variety
  ✅ Duplicate password detection
"""

import secrets
import string
import os
import time
import threading
from cryptography.fernet import Fernet
import pyperclip
from storage import (
    insert_password, get_all_passwords, get_password_by_id,
    update_password, delete_password_by_id
)
from utils import clear_screen

KEY_FILE = "secret.key"


# ─────────────────────────────────────────────
#  Key Management
# ─────────────────────────────────────────────

def _load_or_create_key() -> Fernet:
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)


fernet = _load_or_create_key()


# ─────────────────────────────────────────────
#  Encrypt / Decrypt helpers
# ─────────────────────────────────────────────

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()


# ─────────────────────────────────────────────
#  Secure Password Generator
# ─────────────────────────────────────────────

def _check_strength(password: str) -> str:
    """Returns a strength label: Weak / Medium / Strong / Very Strong."""
    score = 0
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        return "🔴 Weak"
    elif score <= 3:
        return "🟡 Medium"
    elif score <= 4:
        return "🟢 Strong"
    else:
        return "💪 Very Strong"


def generate_secure_password(length: int) -> str:
    """
    Uses secrets module (cryptographically secure).
    Guarantees at least 1 uppercase, 1 lowercase, 1 digit, 1 symbol.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"

    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))

        if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in "!@#$%^&*()-_=+" for c in password)):
            return password


def _check_duplicate(new_password: str) -> list:
    """Return list of sites that already use this exact password."""
    duplicates = []
    for row in get_all_passwords():
        try:
            existing = decrypt(row["password"])
            if existing == new_password:
                duplicates.append(decrypt(row["site"]))
        except Exception:
            pass
    return duplicates


# ─────────────────────────────────────────────
#  Clipboard copy + auto-clear
# ─────────────────────────────────────────────

def _copy_to_clipboard_with_timer(password: str, delay: int = 30):
    """Copy password to clipboard, then clear it after delay seconds."""
    try:
        pyperclip.copy(password)
        print(f"\n📋 Password copied to clipboard! (auto-clears in {delay}s)")

        def clear_clipboard():
            time.sleep(delay)
            try:
                if pyperclip.paste() == password:
                    pyperclip.copy("")
                    print("\n🧹 Clipboard cleared automatically.")
            except Exception:
                pass

        thread = threading.Thread(target=clear_clipboard, daemon=True)
        thread.start()

    except pyperclip.PyperclipException:
        print("⚠️  Clipboard not available on this system.")


# ─────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────

def _print_entry(index: int, row, show_password: bool = True):
    site     = decrypt(row["site"])
    username = decrypt(row["username"])
    password = decrypt(row["password"]) if show_password else "••••••••"
    strength = _check_strength(decrypt(row["password"])) if show_password else ""
    created  = row["created_at"][:10]

    print(f"\n  [{row['id']}] {site}")
    print(f"      👤 User     : {username}")
    if show_password:
        print(f"      🔑 Password : {password}  {strength}")
    else:
        print(f"      🔑 Password : {password}")
    print(f"      📅 Saved    : {created}")


# ─────────────────────────────────────────────
#  CRUD Operations
# ─────────────────────────────────────────────

def add_password():
    clear_screen()
    print("=== Add New Password ===\n")

    site = input("Site name (e.g. Gmail, GitHub): ").strip()
    if not site:
        print("Site name cannot be empty.")
        input("\nPress Enter to continue...")
        return

    username = input("Username / Email: ").strip()
    if not username:
        print("Username cannot be empty.")
        input("\nPress Enter to continue...")
        return

    print("\nGenerate password or enter your own?")
    print("  1. Generate secure password")
    print("  2. Enter my own password")
    choice = input("Choice: ").strip()

    if choice == "1":
        while True:
            try:
                length = int(input("Password length (min 12): ").strip())
                if length < 12:
                    print("Minimum length is 12.")
                    continue
                break
            except ValueError:
                print("Please enter a number.")

        password = generate_secure_password(length)
        print(f"\n✨ Generated: {password}")
        print(f"   Strength : {_check_strength(password)}")

    elif choice == "2":
        password = input("Enter your password: ").strip()
        if not password:
            print("Password cannot be empty.")
            input("\nPress Enter to continue...")
            return
        print(f"   Strength : {_check_strength(password)}")
    else:
        print("Invalid choice.")
        input("\nPress Enter to continue...")
        return

    # Duplicate check
    duplicates = _check_duplicate(password)
    if duplicates:
        sites_str = ", ".join(duplicates)
        print(f"\n⚠️  Warning: This password is already used for: {sites_str}")
        confirm = input("Save anyway? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return

    insert_password(encrypt(site), encrypt(username), encrypt(password))
    print(f"\n✅ Password for '{site}' saved securely!")

    copy = input("Copy password to clipboard? (y/n): ").strip().lower()
    if copy == "y":
        _copy_to_clipboard_with_timer(password)

    input("\nPress Enter to continue...")


def view_passwords():
    clear_screen()
    print("=== Stored Passwords ===\n")

    rows = get_all_passwords()
    if not rows:
        print("No passwords stored yet.")
        input("\nPress Enter to continue...")
        return

    for i, row in enumerate(rows, 1):
        _print_entry(i, row, show_password=True)

    print(f"\n─── Total: {len(rows)} entries ───")

    print("\nEnter an ID to copy its password, or press Enter to go back: ", end="")
    pick = input().strip()
    if pick.isdigit():
        row = get_password_by_id(int(pick))
        if row:
            pw = decrypt(row["password"])
            _copy_to_clipboard_with_timer(pw)
        else:
            print("ID not found.")

    input("\nPress Enter to continue...")


def search_password():
    clear_screen()
    print("=== Search Passwords ===\n")

    query = input("Search by site name: ").strip().lower()
    if not query:
        input("\nPress Enter to continue...")
        return

    rows = get_all_passwords()
    results = []
    for row in rows:
        try:
            site = decrypt(row["site"])
            if query in site.lower():
                results.append(row)
        except Exception:
            pass

    if not results:
        print(f"\nNo results found for '{query}'.")
    else:
        print(f"\n Found {len(results)} result(s):\n")
        for i, row in enumerate(results, 1):
            _print_entry(i, row, show_password=True)

        print("\nEnter an ID to copy password, or press Enter to go back: ", end="")
        pick = input().strip()
        if pick.isdigit():
            row = get_password_by_id(int(pick))
            if row:
                pw = decrypt(row["password"])
                _copy_to_clipboard_with_timer(pw)

    input("\nPress Enter to continue...")


def edit_password():
    clear_screen()
    print("=== Edit Password ===\n")

    rows = get_all_passwords()
    if not rows:
        print("No passwords stored yet.")
        input("\nPress Enter to continue...")
        return

    for i, row in enumerate(rows, 1):
        site = decrypt(row["site"])
        username = decrypt(row["username"])
        print(f"  [{row['id']}] {site} ({username})")

    print()
    entry_id = input("Enter ID to edit (or Enter to cancel): ").strip()
    if not entry_id.isdigit():
        return

    row = get_password_by_id(int(entry_id))
    if not row:
        print("ID not found.")
        input("\nPress Enter to continue...")
        return

    current_site     = decrypt(row["site"])
    current_username = decrypt(row["username"])
    current_password = decrypt(row["password"])

    print(f"\nEditing: {current_site} ({current_username})")
    print("(Press Enter to keep current value)\n")

    new_site = input(f"Site [{current_site}]: ").strip() or current_site
    new_user = input(f"Username [{current_username}]: ").strip() or current_username

    print("  1. Generate new password")
    print("  2. Enter new password manually")
    print("  3. Keep current password")
    pw_choice = input("Choice: ").strip()

    if pw_choice == "1":
        new_password = generate_secure_password(16)
        print(f"\n✨ Generated: {new_password}  {_check_strength(new_password)}")
    elif pw_choice == "2":
        new_password = input("New password: ").strip() or current_password
        print(f"   Strength : {_check_strength(new_password)}")
    else:
        new_password = current_password

    update_password(int(entry_id), encrypt(new_site), encrypt(new_user), encrypt(new_password))
    print(f"\n✅ Entry [{entry_id}] updated successfully!")

    if new_password != current_password:
        copy = input("Copy new password to clipboard? (y/n): ").strip().lower()
        if copy == "y":
            _copy_to_clipboard_with_timer(new_password)

    input("\nPress Enter to continue...")


def delete_password():
    clear_screen()
    print("=== Delete Password ===\n")

    rows = get_all_passwords()
    if not rows:
        print("No passwords stored yet.")
        input("\nPress Enter to continue...")
        return

    for i, row in enumerate(rows, 1):
        site = decrypt(row["site"])
        username = decrypt(row["username"])
        print(f"  [{row['id']}] {site} ({username})")

    print()
    entry_id = input("Enter ID to delete (or Enter to cancel): ").strip()
    if not entry_id.isdigit():
        return

    row = get_password_by_id(int(entry_id))
    if not row:
        print("ID not found.")
        input("\nPress Enter to continue...")
        return

    site = decrypt(row["site"])
    confirm = input(f"\n⚠️  Delete '{site}'? This cannot be undone. (yes/no): ").strip().lower()

    if confirm == "yes":
        delete_password_by_id(int(entry_id))
        print(f"✅ '{site}' deleted.")
    else:
        print("Cancelled.")

    input("\nPress Enter to continue...")