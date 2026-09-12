import pytest
from backend.app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token

def test_password_hashing():
    pwd = "secure_officer_pwd_123"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_generation_and_decoding():
    payload = {"sub": "test_officer", "role": "LAND_RECORD_OFFICER"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    assert len(token) > 20

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "test_officer"
    assert decoded.get("role") == "LAND_RECORD_OFFICER"

def test_invalid_jwt_token():
    decoded = decode_access_token("invalid.jwt.token.string")
    assert decoded is None
