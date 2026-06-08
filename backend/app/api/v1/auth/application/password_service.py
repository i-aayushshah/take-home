"""Password hashing and verification."""

import bcrypt


class PasswordService:
    """Hashes and verifies passwords using bcrypt."""

    def hash_password(self, plain_password: str) -> str:
        """Return a bcrypt hash for the given plain-text password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Return True when the plain password matches the stored hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
