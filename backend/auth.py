"""Password hashing and verification for Campus Customs accounts.

Two hash formats live in the database:

* New accounts (this app) use a **self-describing** PBKDF2 string that carries
  every parameter needed to verify it, so no out-of-band config is required:

      pbkdf2_sha256$<iterations>$<salt_hex>$<digest_hex>      (4 segments)

* The 3 seeded course users use a **legacy** string that does NOT carry the
  iteration count:

      pbkdf2_sha256$<salt>$<digest_hex>                       (3 segments)

  Verifying those needs the iteration count from the course staff. It is read
  from CAMPUS_CUSTOMS_LEGACY_PBKDF2_ITERATIONS (see config). Until that value is
  set, legacy verification raises LegacyIterationsUnknown instead of guessing.

After a successful login, a legacy hash can be upgraded to the new format with
needs_migration() + hash_password(); see the login route in main.py.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from config import LEGACY_PBKDF2_ITERATIONS

ALGORITHM = "pbkdf2_sha256"
NEW_HASH_ITERATIONS = 600_000  # OWASP 2023 guidance for PBKDF2-HMAC-SHA256
SALT_BYTES = 16


class LegacyIterationsUnknown(RuntimeError):
    """Raised when a legacy (3-part) hash must be verified but the iteration
    count has not been configured yet."""


def hash_password(password: str, *, iterations: int = NEW_HASH_ITERATIONS) -> str:
    """Hash a password in the new self-describing format."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"{ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def _verify_new(password: str, iterations: str, salt_hex: str, digest_hex: str) -> bool:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
    return hmac.compare_digest(digest.hex(), digest_hex)


def _verify_legacy(password: str, salt: str, digest_hex: str) -> bool:
    if LEGACY_PBKDF2_ITERATIONS is None:
        raise LegacyIterationsUnknown(
            "Legacy pbkdf2_sha256 hash cannot be verified: set "
            "CAMPUS_CUSTOMS_LEGACY_PBKDF2_ITERATIONS to the course seed value."
        )
    # Legacy salt was stored as a plain string, used as its UTF-8 bytes.
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), LEGACY_PBKDF2_ITERATIONS)
    return hmac.compare_digest(digest.hex(), digest_hex)


def is_legacy_hash(stored: str) -> bool:
    """A legacy hash is the 3-segment form with no iteration count."""
    return stored.startswith(f"{ALGORITHM}$") and stored.count("$") == 2


# A legacy hash should be re-hashed into the new format after a successful login.
needs_migration = is_legacy_hash


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against either hash format.

    Raises LegacyIterationsUnknown for a legacy hash when the iteration count
    is not configured, so the caller can report "pending" rather than a plain
    wrong-password failure.
    """
    parts = stored.split("$")
    if len(parts) == 4 and parts[0] == ALGORITHM and parts[1].isdigit():
        return _verify_new(password, parts[1], parts[2], parts[3])
    if len(parts) == 3 and parts[0] == ALGORITHM:
        return _verify_legacy(password, parts[1], parts[2])
    return False
