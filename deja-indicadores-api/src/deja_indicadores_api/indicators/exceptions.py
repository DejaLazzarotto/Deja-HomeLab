from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class IndicatorNotFoundError(ResourceNotFoundError):
    """Indicador solicitado não encontrado."""

    error_code = "indicator_not_found"

    def __init__(self, indicator_id: str) -> None:
        super().__init__(
            f"Indicador com ID '{indicator_id}' não encontrado."
        )


class IndicatorNameAlreadyExistsError(ResourceConflictError):
    """Nome de indicador já utilizado pela empresa."""

    error_code = "indicator_name_already_exists"

    def __init__(self, company_id: str, name: str) -> None:
        super().__init__(
            f"A empresa com ID '{company_id}' já possui "
            f"um indicador chamado '{name}'."
        )


class CompanyHasIndicatorsError(ResourceConflictError):
    """Empresa possui indicadores e não pode ser excluída."""

    error_code = "company_has_indicators"

    def __init__(self, company_id: str) -> None:
        super().__init__(
            f"A empresa com ID '{company_id}' possui indicadores "
            "cadastrados e não pode ser excluída."
        )