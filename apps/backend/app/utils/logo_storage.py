"""
Company logo persistence — binary storage in the database.

Logos are stored as compressed image bytes (company_logo_data) so they survive
Render restarts. Ephemeral /uploads/ paths and oversized data URLs in
company_logo_url are migrated or cleared.
"""

from __future__ import annotations

import base64
import logging
import re
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger("quotmate.logo")

_DATA_URL_RE = re.compile(r"^data:(image/[\w.+-]+);base64,(.+)$", re.DOTALL)
_MIN_DATA_URL_LENGTH = 800


def prepare_logo_bytes(file_bytes: bytes) -> Tuple[str, bytes]:
    """Resize and compress an uploaded logo for database storage."""
    img = Image.open(BytesIO(file_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img.thumbnail((160, 160), Image.Resampling.LANCZOS)
    output = BytesIO()
    img.save(output, format="WEBP", quality=80, method=4)
    return "image/webp", output.getvalue()


def is_ephemeral_logo_url(url: Optional[str]) -> bool:
    """True for local upload paths that disappear when Render restarts."""
    if not url:
        return False
    value = url.strip()
    if value.startswith("/uploads/"):
        return True
    if "/uploads/" in value:
        return True
    return False


def is_durable_external_url(url: Optional[str]) -> bool:
    """True for CDN / cloud URLs that survive server restarts."""
    if not url or not url.strip():
        return False
    value = url.strip()
    if is_ephemeral_logo_url(value):
        return False
    if value.startswith("data:"):
        return len(value) >= _MIN_DATA_URL_LENGTH
    return value.startswith("http://") or value.startswith("https://")


def user_has_logo(user: User) -> bool:
    if user.company_logo_data:
        return True
    return is_durable_external_url(user.company_logo_url)


def get_logo_bytes(user: User) -> Optional[Tuple[str, bytes]]:
    if user.company_logo_data and user.company_logo_mime:
        return user.company_logo_mime, bytes(user.company_logo_data)
    return None


def get_company_logo_data_uri(user: User) -> Optional[str]:
    """Data URI for PDF templates and previews."""
    stored = get_logo_bytes(user)
    if stored:
        mime, data = stored
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    if is_durable_external_url(user.company_logo_url):
        return user.company_logo_url
    return None


def set_user_logo(user: User, file_bytes: bytes) -> Tuple[str, bytes]:
    """Persist logo bytes on the user and clear legacy URL fields."""
    mime, data = prepare_logo_bytes(file_bytes)
    user.company_logo_mime = mime
    user.company_logo_data = data
    user.company_logo_url = None
    return mime, data


def clear_user_logo(user: User) -> None:
    user.company_logo_mime = None
    user.company_logo_data = None
    user.company_logo_url = None


def _decode_data_url(data_url: str) -> Optional[Tuple[str, bytes]]:
    match = _DATA_URL_RE.match(data_url.strip())
    if not match:
        return None
    mime, b64_part = match.group(1), match.group(2)
    try:
        return mime, base64.b64decode(b64_part)
    except Exception:
        return None


def migrate_legacy_logo(user: User, db: Session) -> None:
    """
    Move legacy data URLs into binary columns; drop dead /uploads/ references.
    """
    changed = False

    if user.company_logo_data:
        if user.company_logo_url and (
            user.company_logo_url.startswith("data:")
            or is_ephemeral_logo_url(user.company_logo_url)
        ):
            user.company_logo_url = None
            changed = True
    elif user.company_logo_url:
        if is_ephemeral_logo_url(user.company_logo_url):
            logger.info("clearing_ephemeral_logo user_id=%s", user.id)
            user.company_logo_url = None
            changed = True
        elif user.company_logo_url.startswith("data:"):
            decoded = _decode_data_url(user.company_logo_url)
            if decoded:
                mime, data = decoded
                user.company_logo_mime = mime
                user.company_logo_data = data
                user.company_logo_url = None
                changed = True
                logger.info("migrated_data_url_logo user_id=%s bytes=%s", user.id, len(data))
            elif len(user.company_logo_url) < _MIN_DATA_URL_LENGTH:
                user.company_logo_url = None
                changed = True

    if changed:
        db.commit()
        db.refresh(user)


def verify_logo_saved(user: User, expected_size: int) -> None:
    if not user.company_logo_data:
        raise ValueError("Logo was not saved to the database.")
    actual = len(user.company_logo_data)
    if actual < expected_size * 0.9:
        raise ValueError(
            f"Logo bytes truncated in database ({actual} vs {expected_size}). "
            "Check database column types."
        )


def ensure_logo_columns(engine: Engine) -> None:
    """Ensure logo-related columns exist and company_logo_url is wide enough."""
    dialect = engine.dialect.name
    try:
        with engine.begin() as conn:
            if dialect == "mysql":
                conn.execute(
                    text(
                        "ALTER TABLE users MODIFY company_logo_url LONGTEXT NULL"
                    )
                )
                # Add binary columns if missing (idempotent on MySQL 8+)
                for stmt in (
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                    "company_logo_mime VARCHAR(64) NULL",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                    "company_logo_data LONGBLOB NULL",
                ):
                    try:
                        conn.execute(text(stmt))
                    except Exception:
                        pass
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
        logger.info("logo columns verified dialect=%s", dialect)
    except Exception as exc:
        logger.warning("logo column check skipped: %s", exc)
