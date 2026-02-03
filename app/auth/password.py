"""Password hashing with bcrypt."""
import bcrypt


def hash_password(password: str) -> str:
    """Hash password with bcrypt. Returns string suitable for DB."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against hashed. Returns True if match."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
