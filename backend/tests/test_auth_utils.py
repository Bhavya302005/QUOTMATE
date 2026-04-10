"""
Unit tests for auth utilities
Tests password hashing (bcrypt), JWT token creation/decoding, and edge cases.
"""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Patch settings before importing auth module
import os
os.environ.setdefault("DATABASE_URL", "mysql://test:test@localhost:3306/test_db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests-only")

from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    """Test bcrypt password hashing and verification"""

    def test_hash_returns_string(self):
        result = hash_password("TestPassword123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_is_not_plaintext(self):
        password = "MySecret123"
        hashed = hash_password(password)
        assert hashed != password

    def test_different_passwords_different_hashes(self):
        hash1 = hash_password("Password1")
        hash2 = hash_password("Password2")
        assert hash1 != hash2

    def test_same_password_different_salts(self):
        """Each hash should use a unique salt"""
        hash1 = hash_password("SamePassword123")
        hash2 = hash_password("SamePassword123")
        assert hash1 != hash2  # Different salts = different hashes

    def test_verify_correct_password(self):
        password = "CorrectPassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("CorrectPassword123")
        assert verify_password("WrongPassword456", hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password("SomePassword123")
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and decoding"""

    def test_create_token_returns_string(self):
        token = create_access_token(data={"sub": "user-123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        token = create_access_token(data={"sub": "user-123", "email": "test@example.com"})
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_decode_expired_token(self):
        """Expired token should raise HTTPException 401"""
        token = create_access_token(
            data={"sub": "user-123"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_decode_invalid_token(self):
        """Garbage token should raise HTTPException 401"""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not.a.valid.jwt.token")
        assert exc_info.value.status_code == 401

    def test_custom_expiration(self):
        token = create_access_token(
            data={"sub": "user-123"},
            expires_delta=timedelta(hours=48)
        )
        payload = decode_token(token)
        assert payload["sub"] == "user-123"

    def test_token_contains_exp_claim(self):
        token = create_access_token(data={"sub": "user-123"})
        payload = decode_token(token)
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
