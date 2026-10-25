"""
services/database.py - Lightweight SQLite persistence layer for Parichay.
Handles user accounts, secure authentication storage, and analysis history.
"""
import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parichay.db")


def get_db_connection():
    """Returns a SQLite connection with row_factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        account_type TEXT DEFAULT 'Free Plan',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Analyses history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        candidate_name TEXT NOT NULL,
        role_title TEXT NOT NULL,
        score INTEGER NOT NULL,
        fit_tier TEXT NOT NULL,
        analysis_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully at %s", DB_PATH)


class AuthManager:
    """Manages user registration, authentication, and profile updates."""

    @staticmethod
    def register_user(name: str, email: str, password: str) -> Dict[str, Any]:
        """Registers a new user with secure password hashing."""
        name = name.strip()
        email = email.strip().lower()

        if not name:
            return {"success": False, "message": "Please provide your full name."}
        if not email or "@" not in email:
            return {"success": False, "message": "Please provide a valid email address."}
        if not password or len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters long."}

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "account_type": "Free Plan"
                }
            }
        except sqlite3.IntegrityError:
            return {"success": False, "message": "An account with this email address already exists. Please log in."}
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(email: str, password: str) -> Dict[str, Any]:
        """Verifies email and password against stored password hash."""
        email = email.strip().lower()
        if not email or not password:
            return {"success": False, "message": "Please enter both email and password."}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash, account_type FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"success": False, "message": "No account found with this email address."}

        if not check_password_hash(row["password_hash"], password):
            return {"success": False, "message": "Incorrect password. Please try again."}

        return {
            "success": True,
            "user": {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "account_type": row["account_type"]
            }
        }

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves user profile by ID."""
        if not user_id:
            return None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, account_type, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    @staticmethod
    def update_profile(user_id: int, name: str, email: str, new_password: str = "") -> Dict[str, Any]:
        """Updates user name, email, and optionally password."""
        name = name.strip()
        email = email.strip().lower()
        if not name or not email:
            return {"success": False, "message": "Name and email cannot be empty."}

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if new_password and len(new_password) >= 6:
                p_hash = generate_password_hash(new_password)
                cursor.execute(
                    "UPDATE users SET name = ?, email = ?, password_hash = ? WHERE id = ?",
                    (name, email, p_hash, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name = ?, email = ? WHERE id = ?",
                    (name, email, user_id)
                )
            conn.commit()
            return {"success": True, "message": "Profile updated successfully."}
        except sqlite3.IntegrityError:
            return {"success": False, "message": "Email is already taken by another account."}
        finally:
            conn.close()


class HistoryManager:
    """Manages saving and loading user analysis history."""

    @staticmethod
    def save_analysis(
        user_id: Optional[int],
        filename: str,
        candidate_name: str,
        role_title: str,
        score: int,
        fit_tier: str,
        analysis_data: Dict[str, Any]
    ) -> Optional[int]:
        """Saves a completed analysis record."""
        if not user_id:
            return None  # Anonymous users don't persist to user history

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO analyses 
                (user_id, filename, candidate_name, role_title, score, fit_tier, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    filename,
                    candidate_name,
                    role_title or "Target Role",
                    score,
                    fit_tier,
                    json.dumps(analysis_data)
                )
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error("Failed to save analysis history: %s", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_analyses(user_id: int) -> List[Dict[str, Any]]:
        """Returns list of past analyses for a user (without heavy JSON payload)."""
        if not user_id:
            return []
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, filename, candidate_name, role_title, score, fit_tier, created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_analysis_by_id(analysis_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves full analysis payload for a specific history item."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, filename, candidate_name, role_title, score, fit_tier, analysis_data, created_at
            FROM analyses
            WHERE id = ? AND user_id = ?
            """,
            (analysis_id, user_id)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None

        result = dict(row)
        try:
            result["analysis_data"] = json.loads(result["analysis_data"])
        except Exception:
            pass
        return result

    @staticmethod
    def delete_analysis(analysis_id: int, user_id: int) -> bool:
        """Deletes an analysis record for the authenticated user."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


# Initialize tables automatically when imported
init_db()
