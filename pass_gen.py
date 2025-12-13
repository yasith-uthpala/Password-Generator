import random
import os
import hashlib
from cryptography.fernet import Fernet

# ---------------- MASTER PASSWORD ----------------

def setup_master_password():
    master = input("Create MASTER password: ")
    hashed = hashlib.sha256(master.encode()).hexdigest()
    with open("master.hash", "w") as f:
        f.write(hashed)
    print("Master password set successfully!\n")


def verify_master_password():
    entered = input("Enter MASTER password to continue: ")
    entered_hash = hashlib.sha256(entered.encode()).hexdigest()

    with open("master.hash", "r") as f:
        stored_hash = f.read()

    return entered_hash == stored_hash


# ---------------- KEY SETUP ----------------

if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)
else:
    with open("secret.key", "rb") as f:
        key = f.read()

fernet = Fernet(key)

# ---------------- PASSWORD FUNCTIONS ----------------

def generate_password():
    site = input("Enter site name (Gmail, Facebook): ")
    username = input("Enter username/email: ")

    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"

    try:
        length = int(input("Enter password length (min 8): "))
    except ValueError:
        print("Numbers only!\n")
        return

    if length < 8:
        print("Password too short!\n")
        return

    password = ""
    for _ in range(length):
        password += random.choice(characters)

    print("\nGenerated Password (save this):", password)

    encrypted = fernet.encrypt(password.encode()).decode()

    with open("passwords.txt", "a") as f:
        f.write(f"{site} | {username} | {encrypted}\n")

    print("Password stored securely!\n")


def view_passwords():
    if not verify_master_password():
        print("Wrong master password! Access denied.\n")
        return

    if not os.path.exists("passwords.txt"):
        print("No passwords stored yet.\n")
        return

    print("\n Stored Passwords:\n")

    with open("passwords.txt", "r") as f:
        for i, line in enumerate(f, start=1):
            parts = line.strip().split(" | ")
            if len(parts) != 3:
                continue

            site, username, encrypted = parts
            password = fernet.decrypt(encrypted.encode()).decode()

            print(f"{i}. Site: {site}")
            print(f"   User: {username}")
            print(f"   Pass: {password}\n")


# ---------------- FIRST RUN CHECK ----------------

if not os.path.exists("master.hash"):
    setup_master_password()

# ---------------- MENU ----------------

while True:
    print("==== Password Manager ====")
    print("1. Add New Password")
    print("2. View Stored Passwords (Protected)")
    print("3. Exit")

    choice = input("Choose option: ")

    if choice == "1":
        generate_password()
    elif choice == "2":
        view_passwords()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice!\n")
