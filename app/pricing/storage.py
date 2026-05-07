import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List

from app.catalog_engine import normalize_model, to_float


DATABASE_URL_ENV = "DATABASE_URL"
SCHEMA_READY = False


def load_env_file() -> None:
    env_path = Path(".env")

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()

        if not text or text.startswith("#") or "=" not in text:
            continue

        key, value = text.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_database_url() -> str:
    load_env_file()
    database_url = os.getenv(DATABASE_URL_ENV, "").strip()

    if not database_url:
        raise RuntimeError(
            "Chưa cấu hình DATABASE_URL cho PostgreSQL. "
            "Ví dụ: postgresql://user:password@localhost:5432/network_quotation"
        )

    return database_url


def load_psycopg():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "Thiếu package psycopg để kết nối PostgreSQL. "
            "Chạy: pip install -r requirements.txt"
        ) from exc

    return psycopg


@contextmanager
def get_connection() -> Iterator[Any]:
    psycopg = load_psycopg()
    global SCHEMA_READY

    with psycopg.connect(get_database_url()) as conn:
        if not SCHEMA_READY:
            ensure_schema(conn)
            SCHEMA_READY = True

        yield conn


def ensure_schema(conn: Any) -> None:
    # PostgreSQL is now the single source of truth for AM/custom prices. The old
    # local SQLite file is intentionally not used, so deployments share one DB.
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_price_entries (
                vendor TEXT NOT NULL,
                model TEXT NOT NULL,
                list_price DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (vendor, model)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS am_prices (
                vendor TEXT NOT NULL,
                model TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (vendor, model)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS app_users (
                id BIGSERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                department TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'user',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_logs (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES app_users(id) ON DELETE SET NULL,
                username TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL DEFAULT '',
                entity_id TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quote_records (
                id BIGSERIAL PRIMARY KEY,
                owner_id BIGINT REFERENCES app_users(id) ON DELETE SET NULL,
                owner_username TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                quote_data JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vendors (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        for column_name in ["full_name", "email", "department", "phone"]:
            cur.execute(
                f"""
                ALTER TABLE app_users
                ADD COLUMN IF NOT EXISTS {column_name} TEXT NOT NULL DEFAULT ''
                """
            )

    conn.commit()


def check_database() -> Dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM custom_price_entries")
            custom_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM am_prices")
            am_count = cur.fetchone()[0]

    return {
        "status": "ok",
        "custom_price_entries": custom_count,
        "am_prices": am_count,
    }


def read_custom_price_entries() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT vendor, model, list_price
                FROM custom_price_entries
                ORDER BY vendor, model
                """
            )
            rows = cur.fetchall()

    return [
        {
            "vendor": row[0],
            "model": row[1],
            "list_price": row[2],
            "rule": "custom_db",
        }
        for row in rows
    ]


def save_custom_price_entry(vendor: str, model: str, price: float) -> None:
    model_key = normalize_model(model)
    final_price = to_float(price, 0)

    if not vendor or not model_key or final_price <= 0:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO custom_price_entries (vendor, model, list_price)
                VALUES (%s, %s, %s)
                ON CONFLICT(vendor, model)
                DO UPDATE SET
                    list_price = excluded.list_price,
                    updated_at = now()
                """,
                (vendor, model_key, final_price),
            )

        conn.commit()


def delete_custom_price_entry(vendor: str, model: str) -> None:
    model_key = normalize_model(model)

    if not vendor or not model_key:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM custom_price_entries
                WHERE lower(vendor) = lower(%s) AND model = %s
                """,
                (vendor, model_key),
            )

        conn.commit()


def read_am_prices() -> Dict[str, float]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT vendor, model, price
                FROM am_prices
                """
            )
            rows = cur.fetchall()

    return {
        f"{row[0].lower()}::{row[1]}": row[2]
        for row in rows
    }


def save_am_price_entry(vendor: str, model: str, price: float) -> None:
    model_key = normalize_model(model)
    final_price = to_float(price, 0)

    if not vendor or not model_key:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            if final_price > 0:
                cur.execute(
                    """
                    INSERT INTO am_prices (vendor, model, price)
                    VALUES (%s, %s, %s)
                    ON CONFLICT(vendor, model)
                    DO UPDATE SET
                        price = excluded.price,
                        updated_at = now()
                    """,
                    (vendor, model_key, final_price),
                )
            else:
                cur.execute(
                    """
                    DELETE FROM am_prices
                    WHERE lower(vendor) = lower(%s) AND model = %s
                    """,
                    (vendor, model_key),
                )

        conn.commit()
