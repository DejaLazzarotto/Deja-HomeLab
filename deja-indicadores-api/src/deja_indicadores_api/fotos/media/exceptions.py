from deja_indicadores_api.core.exceptions import (
    ApplicationError,
    ResourceConflictError,
    ResourceNotFoundError,
)


class FotosMediaNotFoundError(ResourceNotFoundError):
    """Mídia do Deja Fotos não encontrada."""

    error_code = "fotos_media_not_found"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(f"Mídia com ID '{media_id}' não encontrada.")


class FotosMediaAlbumNotFoundError(ResourceNotFoundError):
    """Álbum informado para a mídia não existe."""

    error_code = "fotos_media_album_not_found"

    def __init__(
        self,
        album_id: str,
    ) -> None:
        super().__init__(f"Álbum com ID '{album_id}' não encontrado.")


class FotosMediaAlbumScopeMismatchError(ResourceConflictError):
    """Álbum pertence a outro escopo institucional."""

    error_code = "fotos_media_album_scope_mismatch"

    def __init__(
        self,
        album_id: str,
    ) -> None:
        super().__init__(
            f"O álbum informado não pertence ao mesmo escopo institucional da mídia: {album_id}."
        )


class FotosMediaInvalidTypeError(ApplicationError):
    """Tipo de conteúdo não permitido para o Deja Fotos."""

    error_code = "fotos_media_invalid_type"
    status_code = 415

    def __init__(
        self,
        content_type: str,
    ) -> None:
        super().__init__(f"Tipo de mídia não permitido: {content_type}.")


class FotosMediaInvalidContentError(ApplicationError):
    """Conteúdo físico do arquivo não corresponde a uma mídia válida."""

    error_code = "fotos_media_invalid_content"
    status_code = 422

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
        )


class FotosMediaTooLargeError(ApplicationError):
    """Arquivo excede o limite permitido."""

    error_code = "fotos_media_too_large"
    status_code = 413

    def __init__(
        self,
        max_size_mb: int,
    ) -> None:
        super().__init__(f"A mídia excede o tamanho máximo permitido de {max_size_mb} MB.")


class FotosMediaEmptyFileError(ApplicationError):
    """Arquivo enviado está vazio."""

    error_code = "fotos_media_empty_file"
    status_code = 422

    def __init__(self) -> None:
        super().__init__("O arquivo de mídia enviado está vazio.")


class FotosMediaDuplicateError(ResourceConflictError):
    """Arquivo-fonte já cadastrado no mesmo ambiente."""

    error_code = "fotos_media_duplicate"

    def __init__(
        self,
        existing_media_id: str,
    ) -> None:
        super().__init__(
            "A mídia enviada já está cadastrada "
            f"com o ID '{existing_media_id}'."
        )



class FotosMediaStorageConflictError(ResourceConflictError):
    """O destino calculado para o original já está ocupado."""

    error_code = "fotos_media_storage_conflict"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            "O destino físico calculado para a mídia "
            f"'{media_id}' já está ocupado."
        )


class FotosMediaStorageMoveError(ApplicationError):
    """Falha controlada ao mover o original gerenciado."""

    error_code = "fotos_media_storage_move_failed"
    status_code = 500

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            "Não foi possível reorganizar o arquivo original "
            f"da mídia '{media_id}'."
        )


class FotosMediaDeletionConflictError(ResourceConflictError):
    """Uma mídia em processamento não pode ser removida."""

    error_code = "fotos_media_deletion_processing"

    def __init__(self, media_id: str) -> None:
        super().__init__(
            f"Aguarde o processamento da mídia '{media_id}' antes de excluí-la."
        )


class FotosMediaOriginalDateMissingError(ResourceConflictError):
    """A mídia ainda não possui data original para confirmação."""

    error_code = "fotos_media_original_date_missing"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            "A mídia "
            f"'{media_id}' ainda não possui data original para confirmação."
        )


class FotosMediaDerivativeNotFoundError(ResourceNotFoundError):
    """Arquivo derivado de mídia não encontrado."""

    error_code = "fotos_media_derivative_not_found"

    def __init__(
        self,
        media_id: str,
        derivative_type: str,
    ) -> None:
        super().__init__(
            f"O derivado '{derivative_type}' da mídia "
            f"'{media_id}' não foi encontrado."
        )


class FotosMediaFileNotFoundError(ResourceNotFoundError):
    """Registro existe, mas o original físico não está disponível."""

    error_code = "fotos_media_file_not_found"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            f"O arquivo original da mídia não foi encontrado no armazenamento: {media_id}."
        )



class FotosMediaAlreadyProcessingError(ResourceConflictError):
    """Mídia já possui uma tentativa de processamento em andamento."""

    error_code = "fotos_media_already_processing"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            f"A mídia com ID '{media_id}' já está sendo processada."
        )


class FotosMediaDescriptionNotSupportedError(ResourceConflictError):
    """Descrição editável é suportada apenas para vídeos."""

    error_code = "fotos_media_description_not_supported"

    def __init__(
        self,
        media_id: str,
    ) -> None:
        super().__init__(
            f"A mídia com ID '{media_id}' não é um vídeo e não aceita descrição."
        )
