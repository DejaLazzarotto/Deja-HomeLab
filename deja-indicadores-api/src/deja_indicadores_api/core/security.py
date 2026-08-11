from pwdlib import PasswordHash


class PasswordService:
    """Gera e verifica hashes seguros de senhas."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        """Gera o hash seguro de uma senha em texto puro."""

        return self._password_hash.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        """Verifica uma senha em texto puro contra o hash armazenado."""

        return self._password_hash.verify(password, password_hash)