import hashlib


def hash_password(password: str) -> str:
    """Создает и возвращает SHA-256 хеш пароля."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
