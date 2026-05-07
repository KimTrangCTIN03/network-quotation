import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import Request

from app.pricing.storage import get_connection, load_env_file


SESSION_COOKIE = "nq_session"
SESSION_DAYS = 7
PBKDF2_ITERATIONS = 260_000


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def user_from_row(row: Any) -> Dict[str, Any]:
    return {
        "id": row[0],
        "username": row[1],
        "full_name": row[2],
        "email": row[3],
        "department": row[4],
        "phone": row[5],
        "role": row[6],
        "is_active": row[7],
        "created_at": row[8],
    }


def ensure_default_admin() -> None:
    load_env_file()
    username = os.getenv("ADMIN_USERNAME", "admin").strip() or "admin"
    password = os.getenv("ADMIN_PASSWORD", "admin123").strip() or "admin123"
    sync_password = os.getenv("ADMIN_SYNC_PASSWORD", "").strip().lower() in {"1", "true", "yes"}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM app_users")
            user_count = cur.fetchone()[0]

            if user_count == 0:
                cur.execute(
                    """
                    INSERT INTO app_users (username, password_hash, role, is_active)
                    VALUES (%s, %s, 'admin', TRUE)
                    """,
                    (username, hash_password(password)),
                )
            elif sync_password:
                cur.execute(
                    """
                    UPDATE app_users
                    SET password_hash = %s, role = 'admin', is_active = TRUE, updated_at = now()
                    WHERE lower(username) = lower(%s)
                    """,
                    (hash_password(password), username),
                )

        conn.commit()


def authenticate_user(username: str, password: str) -> Dict[str, Any] | None:
    ensure_default_admin()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, full_name, email, department, phone, role, is_active, created_at, password_hash
                FROM app_users
                WHERE lower(username) = lower(%s)
                """,
                (username.strip(),),
            )
            row = cur.fetchone()

    if not row or not row[7] or not verify_password(password, row[9]):
        return None

    return user_from_row(row)


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_sessions (token, user_id, expires_at)
                VALUES (%s, %s, %s)
                """,
                (token, user_id, expires_at),
            )

        conn.commit()

    return token


def delete_session(token: str) -> None:
    if not token:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_sessions WHERE token = %s", (token,))
        conn.commit()


def log_activity(
    user: Dict[str, Any] | None,
    action: str,
    entity_type: str = "",
    entity_id: str = "",
    detail: str = "",
) -> None:
    user = user or {}

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO activity_logs (user_id, username, action, entity_type, entity_id, detail)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user.get("id"),
                        str(user.get("username") or ""),
                        action,
                        entity_type,
                        str(entity_id or ""),
                        detail,
                    ),
                )
            conn.commit()
    except Exception:
        # Activity logging must never break the user workflow.
        return


def list_activity_logs(limit: int = 80) -> List[Dict[str, Any]]:
    ensure_default_admin()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, action, entity_type, entity_id, detail, created_at
                FROM activity_logs
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "username": row[1],
            "action": row[2],
            "entity_type": row[3],
            "entity_id": row[4],
            "detail": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


def admin_overview() -> Dict[str, Any]:
    ensure_default_admin()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM app_users")
            user_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM app_users WHERE role = 'admin'")
            admin_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM quote_records")
            quote_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM vendors")
            vendor_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM custom_price_entries")
            list_price_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM am_prices")
            am_price_count = cur.fetchone()[0]

    return {
        "user_count": user_count,
        "admin_count": admin_count,
        "quote_count": quote_count,
        "vendor_count": vendor_count,
        "list_price_count": list_price_count,
        "am_price_count": am_price_count,
    }


def quote_from_row(row: Any) -> Dict[str, Any]:
    return {
        "id": row[0],
        "owner_id": row[1],
        "owner_username": row[2],
        "title": row[3],
        "status": row[4],
        "quote_data": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def list_quote_records(user: Dict[str, Any], limit: int = 80) -> List[Dict[str, Any]]:
    ensure_default_admin()
    is_admin = user.get("role") == "admin"

    with get_connection() as conn:
        with conn.cursor() as cur:
            if is_admin:
                cur.execute(
                    """
                    SELECT id, owner_id, owner_username, title, status, quote_data, created_at, updated_at
                    FROM quote_records
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
            else:
                cur.execute(
                    """
                    SELECT id, owner_id, owner_username, title, status, quote_data, created_at, updated_at
                    FROM quote_records
                    WHERE owner_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (user.get("id"), limit),
                )
            rows = cur.fetchall()

    return [quote_from_row(row) for row in rows]


def create_quote_record(user: Dict[str, Any], title: str, quote_data: Dict[str, Any], status: str = "draft") -> Dict[str, Any]:
    clean_status = status if status in {"draft", "submitted", "approved", "locked"} else "draft"
    clean_title = title.strip() or "Bao gia moi"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO quote_records (owner_id, owner_username, title, status, quote_data)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                RETURNING id, owner_id, owner_username, title, status, quote_data, created_at, updated_at
                """,
                (
                    user.get("id"),
                    user.get("username") or "",
                    clean_title,
                    clean_status,
                    json.dumps(quote_data),
                ),
            )
            row = cur.fetchone()
        conn.commit()

    return quote_from_row(row)


def update_quote_status(user: Dict[str, Any], quote_id: int, status: str) -> Dict[str, Any]:
    if user.get("role") != "admin":
        raise PermissionError("Admin permission required")

    clean_status = status if status in {"draft", "submitted", "approved", "locked"} else "draft"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE quote_records
                SET status = %s, updated_at = now()
                WHERE id = %s
                RETURNING id, owner_id, owner_username, title, status, quote_data, created_at, updated_at
                """,
                (clean_status, quote_id),
            )
            row = cur.fetchone()
        conn.commit()

    if not row:
        raise ValueError("Quote not found")

    return quote_from_row(row)


def get_current_user(request: Request) -> Dict[str, Any] | None:
    token = request.cookies.get(SESSION_COOKIE, "")
    if not token:
        return None

    ensure_default_admin()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM user_sessions
                WHERE expires_at < now()
                """
            )
            cur.execute(
                """
                SELECT u.id, u.username, u.full_name, u.email, u.department, u.phone, u.role, u.is_active, u.created_at
                FROM user_sessions s
                JOIN app_users u ON u.id = s.user_id
                WHERE s.token = %s AND s.expires_at >= now()
                """,
                (token,),
            )
            row = cur.fetchone()
        conn.commit()

    if not row or not row[7]:
        return None

    return user_from_row(row)


def list_users() -> List[Dict[str, Any]]:
    ensure_default_admin()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, full_name, email, department, phone, role, is_active, created_at
                FROM app_users
                ORDER BY id
                """
            )
            rows = cur.fetchall()

    return [user_from_row(row) for row in rows]


def create_user(
    username: str,
    password: str,
    role: str,
    is_active: bool = True,
    full_name: str = "",
    email: str = "",
    department: str = "",
    phone: str = "",
) -> None:
    clean_username = username.strip()
    clean_role = role if role in {"admin", "user"} else "user"

    if not clean_username or not password:
        raise ValueError("Username va password la bat buoc.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app_users (
                    username, password_hash, full_name, email, department, phone, role, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    clean_username,
                    hash_password(password),
                    full_name.strip(),
                    email.strip(),
                    department.strip(),
                    phone.strip(),
                    clean_role,
                    is_active,
                ),
            )
        conn.commit()


def update_profile(
    user_id: int,
    full_name: str = "",
    email: str = "",
    department: str = "",
    phone: str = "",
    password: str = "",
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            if password:
                cur.execute(
                    """
                    UPDATE app_users
                    SET
                        full_name = %s,
                        email = %s,
                        department = %s,
                        phone = %s,
                        password_hash = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (
                        full_name.strip(),
                        email.strip(),
                        department.strip(),
                        phone.strip(),
                        hash_password(password),
                        user_id,
                    ),
                )
            else:
                cur.execute(
                    """
                    UPDATE app_users
                    SET
                        full_name = %s,
                        email = %s,
                        department = %s,
                        phone = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (
                        full_name.strip(),
                        email.strip(),
                        department.strip(),
                        phone.strip(),
                        user_id,
                    ),
                )
        conn.commit()


def update_user(
    user_id: int,
    role: str,
    is_active: bool,
    password: str = "",
    full_name: str = "",
    email: str = "",
    department: str = "",
    phone: str = "",
) -> None:
    clean_role = role if role in {"admin", "user"} else "user"

    with get_connection() as conn:
        with conn.cursor() as cur:
            if password:
                cur.execute(
                    """
                    UPDATE app_users
                    SET
                        full_name = %s,
                        email = %s,
                        department = %s,
                        phone = %s,
                        role = %s,
                        is_active = %s,
                        password_hash = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (
                        full_name.strip(),
                        email.strip(),
                        department.strip(),
                        phone.strip(),
                        clean_role,
                        is_active,
                        hash_password(password),
                        user_id,
                    ),
                )
            else:
                cur.execute(
                    """
                    UPDATE app_users
                    SET
                        full_name = %s,
                        email = %s,
                        department = %s,
                        phone = %s,
                        role = %s,
                        is_active = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (
                        full_name.strip(),
                        email.strip(),
                        department.strip(),
                        phone.strip(),
                        clean_role,
                        is_active,
                        user_id,
                    ),
                )

        conn.commit()
