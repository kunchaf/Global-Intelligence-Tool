import secrets
import time
from threading import Lock

_store: dict[str, tuple[float, dict]] = {}
_lock = Lock()
TTL_SEC = 3600
_MAX_KEYS = 500


def _prune_locked(now: float) -> None:
    if len(_store) <= _MAX_KEYS:
        return
    expired = [k for k, (ts, _) in _store.items() if now - ts > TTL_SEC]
    for k in expired:
        _store.pop(k, None)
    if len(_store) <= _MAX_KEYS:
        return
    for k, _ in sorted(_store.items(), key=lambda x: x[1][0])[: len(_store) // 2]:
        _store.pop(k, None)


def store_compare_payload(payload: dict) -> str:
    key = secrets.token_urlsafe(16)
    now = time.time()
    with _lock:
        _prune_locked(now)
        _store[key] = (now, payload)
    return key


def get_compare_payload(key: str | None) -> dict | None:
    if not key:
        return None
    now = time.time()
    with _lock:
        tup = _store.get(key)
        if not tup:
            return None
        ts, payload = tup
        if now - ts > TTL_SEC:
            _store.pop(key, None)
            return None
        return payload
