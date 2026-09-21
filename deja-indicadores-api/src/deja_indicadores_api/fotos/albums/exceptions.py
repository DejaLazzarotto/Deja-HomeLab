from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class FotosAlbumNotFoundError(ResourceNotFoundError):
    """Álbum do Deja Fotos não encontrado."""

    error_code = "fotos_album_not_found"

    def __init__(
        self,
        album_id: str,
    ) -> None:
        super().__init__(
            f"Álbum com ID '{album_id}' não encontrado."
        )


class FotosAlbumPeriodNotFoundError(ResourceNotFoundError):
    """O álbum não possui mídias no período informado."""

    error_code = "fotos_album_period_not_found"

    def __init__(
        self,
        album_id: str,
        year: int,
        month: int,
    ) -> None:
        super().__init__(
            "O álbum com ID "
            f"'{album_id}' não possui mídias no período "
            f"{month:02d}/{year:04d}."
        )


class FotosAlbumAlreadyExistsError(ResourceConflictError):
    """Já existe um álbum com o mesmo nome no mesmo escopo."""

    error_code = "fotos_album_already_exists"

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(
            f"Já existe um álbum chamado '{name}' neste ambiente."
        )


class FotosAlbumHasMediaError(ResourceConflictError):
    """O álbum possui mídias vinculadas e não pode ser excluído."""

    error_code = "fotos_album_has_media"

    def __init__(
        self,
        album_id: str,
    ) -> None:
        super().__init__(
            f"O álbum com ID '{album_id}' possui mídias vinculadas."
        )