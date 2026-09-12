import hashlib
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False
    salt = "sih2026_dolr_salt"
    sha_hash = hashlib.sha256((plain_password + salt).encode("utf-8")).hexdigest()
    return sha_hash == hashed_password

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_file_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
