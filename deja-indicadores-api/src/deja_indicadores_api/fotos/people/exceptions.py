"""Erros de domínio de Pessoas do Deja Fotos."""

from deja_indicadores_api.core.exceptions import (
    ApplicationError,
    ResourceConflictError,
    ResourceNotFoundError,
)


class FotosPersonNotFoundError(ResourceNotFoundError):
    """Pessoa não encontrada."""

    error_code = "fotos_person_not_found"

    def __init__(self, person_id: str) -> None:
        super().__init__(
            f"Pessoa com ID '{person_id}' não encontrada."
        )


class FotosPersonAlreadyExistsError(ResourceConflictError):
    """Nome já cadastrado no mesmo ambiente."""

    error_code = "fotos_person_already_exists"

    def __init__(self, name: str) -> None:
        super().__init__(
            f"Já existe uma pessoa chamada '{name}' neste ambiente."
        )


class FotosPersonMediaScopeMismatchError(ResourceConflictError):
    """Pessoa e mídia pertencem a escopos diferentes."""

    error_code = "fotos_person_media_scope_mismatch"

    def __init__(self) -> None:
        super().__init__(
            "A pessoa e a mídia devem pertencer ao mesmo ambiente."
        )


class FotosPersonMediaAlreadyLinkedError(ResourceConflictError):
    """A mídia já está vinculada à pessoa."""

    error_code = "fotos_person_media_already_linked"

    def __init__(self) -> None:
        super().__init__(
            "Esta mídia já está vinculada à pessoa."
        )


class FotosPersonMediaLinkNotFoundError(ResourceNotFoundError):
    """Vínculo pessoa–mídia não encontrado."""

    error_code = "fotos_person_media_link_not_found"

    def __init__(self) -> None:
        super().__init__(
            "Esta mídia não está vinculada à pessoa."
        )


class FotosPersonAvatarNotFoundError(ResourceNotFoundError):
    """A pessoa não possui avatar disponível."""

    error_code = "fotos_person_avatar_not_found"

    def __init__(self) -> None:
        super().__init__(
            "O avatar da pessoa não está disponível."
        )


class FotosPersonAvatarInvalidError(ApplicationError):
    """Arquivo enviado não é uma imagem de avatar válida."""

    error_code = "fotos_person_avatar_invalid"
    status_code = 422

    def __init__(self) -> None:
        super().__init__(
            "Envie uma imagem JPEG, PNG ou WebP válida."
        )


class FotosPersonAvatarTooLargeError(ApplicationError):
    """Avatar excede o tamanho permitido."""

    error_code = "fotos_person_avatar_too_large"
    status_code = 413

    def __init__(self) -> None:
        super().__init__(
            "O avatar deve ter no máximo 10 MB."
        )