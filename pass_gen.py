"""
Advanced Password Manager
Entry point - run this file to start the app.
"""

from auth import setup_master_password, verify_master_password, check_lockout
from vault import add_password, view_passwords, search_password, delete_password, edit_password
from utils import clear_screen
import os


def main_menu():
    clear_screen()
    print("╔══════════════════════════════╗")
    print("║     🔐 Password Manager      ║")
    print("╠══════════════════════════════╣")
    print("║  1. Add New Password         ║")
    print("║  2. View All Passwords       ║")
    print("║  3. Search Password          ║")
    print("║  4. Edit Password            ║")
    print("║  5. Delete Password          ║")
    print("║  6. Exit                     ║")
    print("╚══════════════════════════════╝")
    return input("Choose option: ").strip()


def main():
    if not os.path.exists("master.hash"):
        clear_screen()
        print("=== First Time Setup ===")
        setup_master_password()

    clear_screen()
    print("=== Password Manager - Login ===")

    if not check_lockout():
        return

    if not verify_master_password():
        return

    while True:
        choice = main_menu()

        if choice == "1":
            add_password()
        elif choice == "2":
            view_passwords()
        elif choice == "3":
            search_password()
        elif choice == "4":
            edit_password()
        elif choice == "5":
            delete_password()
        elif choice == "6":
            print("\nGoodbye! Stay secure. 👋")
            break
        else:
            print("Invalid choice. Try again.\n")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()