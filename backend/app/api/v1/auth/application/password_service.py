"""Password hashing and verification."""

from passlib.context import CryptContext

_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Hashes and verifies passwords using bcrypt."""

    def hash_password(self, plain_password: str) -> str:
        """Return a bcrypt hash for the given plain-text password."""
        return _context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Return True when the plain password matches the stored hash."""
        return _context.verify(plain_password, hashed_password)
