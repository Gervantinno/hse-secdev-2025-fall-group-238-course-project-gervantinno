import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def _load_file_backend(path: str) -> dict:
    """Load a JSON file that acts as a local secrets backend (dev/test only).

    The JSON file should map secret names to values, e.g. {"DB_PASSWORD": "..."}.
    This is a safe, deterministic fallback for local development and tests.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("failed to load secrets backend file %s: %s", path, exc)
        return {}


def get_secret(name: str) -> str:
    """Return a secret by name.

    Resolution order:
      1. Environment variable with the given name.
      2. Local JSON backend if env var `VAULT_BACKEND_FILE` is set (dev only).

    Raises KeyError if the secret cannot be found.
    """
    val = os.getenv(name)
    if val:
        return val

    backend = os.getenv("VAULT_BACKEND_FILE")
    if backend:
        store = _load_file_backend(backend)
        if name in store:
            return store[name]

    raise KeyError(f"secret not found: {name}")


def mask_secret(value: Optional[str]) -> str:
    """Return a masked representation safe for logs (no secret material)."""
    if value is None:
        return "<missing>"
    return f"<masked len={len(value)}>"


def init_vault_client():
    """Placeholder for integrating with Vault/KMS in production.

    Real integration should be added according to ADR-003 (use hvac or hvault client
    and proper auth). This function intentionally does not perform remote calls.
    """
    raise NotImplementedError("Vault client integration not implemented in this repo")
