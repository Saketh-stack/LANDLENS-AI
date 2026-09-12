import hashlib

def hash_password(password: str) -> str:
    # Safe SHA256-salt hashing compatible with Python 3.14
    salt = "sih2026_dolr_salt"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password
