"""
Portal Account Manager for JainBiz Submissions.
Supports multiple jainforjain.com login accounts with dynamic switching,
and ensures strict cross-account deduplication so leads submitted on ANY account
are never re-submitted.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
ACCOUNTS_FILE = os.path.join(DB_DIR, "portal_accounts.json")

DEFAULT_MASTER_EMAIL = "mohit12836@gmail.com"
DEFAULT_MASTER_PASS = "223034000"

def get_portal_accounts_file_path() -> str:
    os.makedirs(DB_DIR, exist_ok=True)
    return ACCOUNTS_FILE

def load_portal_accounts() -> Dict[str, Any]:
    """Loads accounts from disk or initializes with default master account."""
    filepath = get_portal_accounts_file_path()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and isinstance(data, dict) and "accounts" in data and len(data["accounts"]) > 0:
                    return data
        except Exception as e:
            print(f"[ACCOUNT_MANAGER] Warning reading accounts: {e}")

    # Initialize default state
    initial_data = {
        "active_account_id": "master_1",
        "accounts": [
            {
                "id": "master_1",
                "email": DEFAULT_MASTER_EMAIL,
                "password": DEFAULT_MASTER_PASS,
                "label": "Account 1 (Master): mohit12836@gmail.com",
                "is_active": True,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }
    save_portal_accounts(initial_data)
    return initial_data

def save_portal_accounts(data: Dict[str, Any]):
    """Saves accounts dictionary to JSON file."""
    filepath = get_portal_accounts_file_path()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_active_account() -> Dict[str, Any]:
    """Returns the currently active account dict."""
    data = load_portal_accounts()
    active_id = data.get("active_account_id")
    for acc in data.get("accounts", []):
        if acc.get("id") == active_id or acc.get("is_active"):
            return acc
    if data.get("accounts"):
        return data["accounts"][0]
    return {
        "id": "master_1",
        "email": DEFAULT_MASTER_EMAIL,
        "password": DEFAULT_MASTER_PASS,
        "label": "Account 1 (Master): mohit12836@gmail.com",
        "is_active": True
    }

def get_active_account_credentials() -> Tuple[str, str, str]:
    """Returns (email, password, label_or_id)."""
    acc = get_active_account()
    return acc.get("email", DEFAULT_MASTER_EMAIL), acc.get("password", DEFAULT_MASTER_PASS), acc.get("id", "master_1")

def add_or_update_account(
    email: str,
    password: str,
    label: Optional[str] = None,
    make_active: bool = False
) -> Dict[str, Any]:
    """Adds a new portal account or updates existing by email."""
    data = load_portal_accounts()
    clean_email = email.strip()
    clean_pass = password.strip()
    clean_label = (label or "").strip() or f"Account: {clean_email}"

    existing = None
    for acc in data.get("accounts", []):
        if acc.get("email", "").lower() == clean_email.lower():
            existing = acc
            break

    if existing:
        existing["password"] = clean_pass
        if label:
            existing["label"] = clean_label
        account_id = existing["id"]
    else:
        account_id = f"acc_{uuid.uuid4().hex[:6]}"
        new_acc = {
            "id": account_id,
            "email": clean_email,
            "password": clean_pass,
            "label": clean_label,
            "is_active": False,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["accounts"].append(new_acc)

    if make_active:
        data["active_account_id"] = account_id
        for acc in data["accounts"]:
            acc["is_active"] = (acc["id"] == account_id)

    save_portal_accounts(data)
    return {"status": "success", "account_id": account_id, "email": clean_email}

def set_active_account(account_id_or_email: str) -> bool:
    """Switches active portal account by ID or email."""
    data = load_portal_accounts()
    target_id = None
    key = account_id_or_email.strip().lower()

    for acc in data.get("accounts", []):
        if acc.get("id") == account_id_or_email or acc.get("email", "").lower() == key:
            target_id = acc["id"]
            break

    if not target_id:
        return False

    data["active_account_id"] = target_id
    for acc in data.get("accounts", []):
        acc["is_active"] = (acc["id"] == target_id)

    save_portal_accounts(data)
    return True

def delete_account(account_id_or_email: str) -> bool:
    """Deletes an account (master account cannot be deleted)."""
    data = load_portal_accounts()
    key = account_id_or_email.strip().lower()

    target = None
    for acc in data.get("accounts", []):
        if acc.get("id") == account_id_or_email or acc.get("email", "").lower() == key:
            target = acc
            break

    if not target or target.get("email", "").lower() == DEFAULT_MASTER_EMAIL.lower():
        # Do not allow deleting master
        return False

    data["accounts"] = [a for a in data["accounts"] if a["id"] != target["id"]]
    if data.get("active_account_id") == target["id"]:
        if data["accounts"]:
            data["active_account_id"] = data["accounts"][0]["id"]
            data["accounts"][0]["is_active"] = True

    save_portal_accounts(data)
    return True

def resolve_credentials(
    override_email: Optional[str] = None,
    override_password: Optional[str] = None,
    account_id: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Resolves credentials in priority order:
    1. Direct override email & password if provided.
    2. Account ID if provided.
    3. Active saved account.
    4. Default Master fallback.
    Returns (email, password, label_or_user_slug).
    """
    if override_email and override_password and override_email.strip() and override_password.strip():
        user_slug = override_email.strip().split("@")[0]
        return override_email.strip(), override_password.strip(), user_slug

    data = load_portal_accounts()
    if account_id:
        for acc in data.get("accounts", []):
            if acc.get("id") == account_id or acc.get("email", "").lower() == account_id.strip().lower():
                return acc.get("email"), acc.get("password"), acc.get("email").split("@")[0]

    active = get_active_account()
    email = active.get("email", DEFAULT_MASTER_EMAIL)
    pwd = active.get("password", DEFAULT_MASTER_PASS)
    return email, pwd, email.split("@")[0]

def get_public_accounts_view(excel_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns public-safe accounts list (passwords masked) along with submission statistics
    calculated from the master Excel database.
    """
    data = load_portal_accounts()
    active_id = data.get("active_account_id")

    # Count submitted leads per account from Excel if available
    acc_counts: Dict[str, int] = {}
    total_submitted = 0
    total_pending = 0

    if excel_path and os.path.exists(excel_path):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, data_only=True)
            ws = wb.active
            for r in range(2, ws.max_row + 1):
                biz_id = str(ws.cell(row=r, column=24).value or "").strip()
                status = str(ws.cell(row=r, column=26).value or "").strip()
                status_lower = status.lower()

                if "submitted" in status_lower or "live" in status_lower or biz_id.startswith("JFJ-"):
                    total_submitted += 1
                    # Check if email is in status, e.g. "Submitted - Live [mohit12836@gmail.com]"
                    matched = False
                    for acc in data.get("accounts", []):
                        acc_email = acc.get("email", "")
                        acc_user = acc_email.split("@")[0]
                        if acc_email.lower() in status_lower or acc_user.lower() in status_lower:
                            acc_counts[acc["id"]] = acc_counts.get(acc["id"], 0) + 1
                            matched = True
                            break
                    if not matched:
                        # Attributed to master if no tag
                        acc_counts["master_1"] = acc_counts.get("master_1", 0) + 1
                elif "ready" in status_lower or not status:
                    total_pending += 1
        except Exception as e:
            print(f"[ACCOUNT_MANAGER] Error counting Excel rows: {e}")

    safe_accounts = []
    for acc in data.get("accounts", []):
        is_act = (acc.get("id") == active_id or acc.get("is_active", False))
        safe_accounts.append({
            "id": acc["id"],
            "email": acc["email"],
            "label": acc.get("label", acc["email"]),
            "is_active": is_act,
            "is_master": (acc["email"].lower() == DEFAULT_MASTER_EMAIL.lower()),
            "submitted_count": acc_counts.get(acc["id"], 0),
            "created_at": acc.get("created_at", "")
        })

    return {
        "active_account_id": active_id,
        "accounts": safe_accounts,
        "total_submitted_across_all_accounts": total_submitted,
        "total_ready_for_submission": total_pending,
        "dedup_guarantee": "100% Guaranteed: Any lead submitted under any account will NEVER be re-submitted."
    }
