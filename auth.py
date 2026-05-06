"""
auth.py - Master password setup, verification, and lockout system.

Improvements applied:
  ✅ bcrypt instead of SHA-256 (salted hashing)
  ✅ Login attempt limiter (lockout after 5 failed tries)
"""

import bcrypt
import json
import os
import time
from utils import clear_screen

MASTER_HASH_FILE = "master.hash"
LOCKOUT_FILE = "lockout.json"

MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes in seconds


# ─────────────────────────────────────────────
#  Lockout Logic
# ─────────────────────────────────────────────

def _load_lockout() -> dict:
    if not os.path.exists(LOCKOUT_FILE):
        return {"attempts": 0, "locked_until": 0}
    with open(LOCKOUT_FILE, "r") as f:
        return json.load(f)


def _save_lockout(data: dict):
    with open(LOCKOUT_FILE, "w") as f:
        json.dump(data, f)


def _reset_lockout():
    _save_lockout({"attempts": 0, "locked_until": 0})


def check_lockout() -> bool:
    """Returns True if user is allowed to proceed, False if locked out."""
    data = _load_lockout()
    now = time.time()

    if data["locked_until"] > now:
        remaining = int(data["locked_until"] - now)
        print(f"\n🔒 Account locked. Try again in {remaining} seconds.")
        return False

    return True


def _record_failed_attempt():
    data = _load_lockout()
    data["attempts"] += 1

    if data["attempts"] >= MAX_ATTEMPTS:
        data["locked_until"] = time.time() + LOCKOUT_DURATION
        print(f"\n⛔ Too many failed attempts! Locked for {LOCKOUT_DURATION // 60} minutes.")
    else:
        remaining_tries = MAX_ATTEMPTS - data["attempts"]
        print(f"❌ Wrong password! {remaining_tries} attempt(s) remaining.")

    _save_lockout(data)


# ─────────────────────────────────────────────
#  Master Password Setup & Verify
# ─────────────────────────────────────────────

def setup_master_password():
    """Create and store the master password using bcrypt."""
    while True:
        master = input("Create MASTER password (min 8 chars): ").strip()
        if len(master) < 8:
            print("⚠️  Password must be at least 8 characters.\n")
            continue

        confirm = input("Confirm MASTER password: ").strip()
        if master != confirm:
            print("⚠️  Passwords do not match. Try again.\n")
            continue

        break

    hashed = bcrypt.hashpw(master.encode(), bcrypt.gensalt())
    with open(MASTER_HASH_FILE, "wb") as f:
        f.write(hashed)

    print("\n✅ Master password set successfully!\n")


def verify_master_password() -> bool:
    """Prompt for master password and verify with bcrypt. Returns True if correct."""
    if not os.path.exists(MASTER_HASH_FILE):
        print("No master password found. Please set one first.")
        return False

    with open(MASTER_HASH_FILE, "rb") as f:
        stored_hash = f.read()

    entered = input("Enter MASTER password: ").strip()
    is_correct = bcrypt.checkpw(entered.encode(), stored_hash)

    if is_correct:
        _reset_lockout()
        print("\n✅ Access granted!\n")
        return True
    else:
        _record_failed_attempt()
        input("\nPress Enter to continue...")
        return False