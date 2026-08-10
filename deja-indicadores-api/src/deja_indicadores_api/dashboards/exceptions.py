from deja_indicadores_api.core.exceptions import ApplicationError


class InvalidDashboardPeriodError(ApplicationError):
    """Período informado para o dashboard é inválido."""

    error_code = "invalid_dashboard_period"

    def __init__(self) -> None:
        super().__init__(
            "A data inicial não pode ser posterior à data final."
        )