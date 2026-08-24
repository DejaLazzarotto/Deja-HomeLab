from collections.abc import Iterable

from deja_indicadores_api.core.exceptions import ApplicationError


class UnknownModuleKeysError(ApplicationError):
    """Uma ou mais chaves não pertencem ao catálogo instalado."""

    error_code = "unknown_module_keys"

    def __init__(self, module_keys: Iterable[str]) -> None:
        sorted_keys = sorted(set(module_keys))
        formatted_keys = ", ".join(
            f"'{module_key}'"
            for module_key in sorted_keys
        )
        super().__init__(
            "As seguintes chaves de módulos não pertencem ao "
            f"catálogo instalado: {formatted_keys}."
        )


class ModuleNotEnabledError(ApplicationError):
    """Módulo não liberado para a organização autenticada."""

    status_code = 403
    error_code = "module_not_enabled"

    def __init__(self, module_key: str) -> None:
        self.module_key = module_key
        super().__init__(
            "O módulo solicitado não está liberado para esta organização."
        )