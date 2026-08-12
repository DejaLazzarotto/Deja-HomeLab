from deja_indicadores_api.core.exceptions import ApplicationError


class AuthenticationError(ApplicationError):
    """Erro-base de autenticação com desafio Bearer."""

    status_code = 401

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthenticationError):
    """Credenciais de acesso inválidas."""

    error_code = "invalid_credentials"

    def __init__(self) -> None:
        super().__init__("Organização, e-mail ou senha inválidos.")


class InactiveUserError(AuthenticationError):
    """Usuário sem permissão para iniciar uma sessão."""

    error_code = "inactive_user"

    def __init__(self) -> None:
        super().__init__("O usuário está inativo.")


class InvalidAccessTokenError(AuthenticationError):
    """Token de acesso ausente, inválido ou sem identidade válida."""

    error_code = "invalid_access_token"

    def __init__(self) -> None:
        super().__init__("Token de acesso inválido.")


class AuthorizationError(ApplicationError):
    """Usuário autenticado sem permissão para executar a operação."""

    status_code = 403
    error_code = "access_forbidden"

    def __init__(self) -> None:
        super().__init__("Acesso não permitido.")