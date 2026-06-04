"""
Company logo persistence helpers.

Logos must be stored in the database (base64 data URLs or durable HTTPS URLs).
Ephemeral /uploads/ paths are cleared on Render restarts and must not be used.
"""

from __future__ import annotations

import base64
import logging
from io import BytesIO
from typing import Optional

from PIL import Image
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger("quotmate.logo")

# WebP thumbnail at 160px is typically several KB as base64 — well above this floor.
_MIN_DATA_URL_LENGTH = 800


def encode_logo_to_data_url(file_bytes: bytes) -> str:
    """Resize and compress a logo image for durable DB storage."""
    img = Image.open(BytesIO(file_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img.thumbnail((160, 160), Image.Resampling.LANCZOS)
    output = BytesIO()
    img.save(output, format="WEBP", quality=80, method=4)
    b64_str = base64.b64encode(output.getvalue()).decode("utf-8")
    return f"data:image/webp;base64,{b64_str}"


def is_valid_persisted_logo(url: Optional[str]) -> bool:
    """Return True if the logo URL can be rendered after a server restart."""
    if not url or not url.strip():
        return False
    value = url.strip()
    if value.startswith("/uploads/"):
        return False
    if value.startswith("data:"):
        return len(value) >= _MIN_DATA_URL_LENGTH
    if value.startswith("http://") or value.startswith("https://"):
        return True
    return False


def sanitize_logo_url(url: Optional[str]) -> Optional[str]:
    """Drop ephemeral or corrupt logo values before sending to clients."""
    if is_valid_persisted_logo(url):
        return url
    return None


def verify_logo_saved(expected: str, actual: Optional[str]) -> None:
    """
    Raise ValueError if the DB did not store the full logo (e.g. VARCHAR truncation).
    """
    if not actual:
        raise ValueError("Logo was not saved to the database.")
    if len(actual) < len(expected) * 0.95:
        raise ValueError(
            f"Logo was truncated in the database ({len(actual)} vs {len(expected)} chars). "
            "Run database migrations: alembic upgrade head"
        )
    if not is_valid_persisted_logo(actual):
        raise ValueError("Logo in database is not in a persistent format.")


def ensure_logo_column_width(engine: Engine) -> None:
    """Widen users.company_logo_url so base64 logos are not truncated."""
    dialect = engine.dialect.name
    try:
        with engine.begin() as conn:
            if dialect == "mysql":
                conn.execute(
                    text(
                        "ALTER TABLE users MODIFY company_logo_url LONGTEXT NULL"
                    )
                )
            elif dialect == "postgresql":
                conn.execute(
                    text(
                        "ALTER TABLE users "
                        "ALTER COLUMN company_logo_url TYPE TEXT"
                    )
                )
            else:
                conn.execute(
                    text(
                        "ALTER TABLE users "
                        "ALTER COLUMN company_logo_url TYPE TEXT"
                    )
                )
        logger.info("company_logo_url column verified for dialect=%s", dialect)
    except Exception as exc:
        # Column may already be wide enough; log and continue.
        logger.warning(
            "Could not widen company_logo_url (may already be OK): %s", exc
        )
