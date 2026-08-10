from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class MeasurementNotFoundError(ResourceNotFoundError):
    """Medição solicitada não encontrada."""

    error_code = "measurement_not_found"

    def __init__(self, measurement_id: str) -> None:
        super().__init__(
            f"Medição com ID '{measurement_id}' não encontrada."
        )


class MeasurementAlreadyExistsError(ResourceConflictError):
    """Medição já cadastrada para o indicador na data de referência."""

    error_code = "measurement_already_exists"

    def __init__(
        self,
        indicator_id: str,
        reference_date: str,
    ) -> None:
        super().__init__(
            f"O indicador com ID '{indicator_id}' já possui uma medição "
            f"na data de referência '{reference_date}'."
        )


class IndicatorHasMeasurementsError(ResourceConflictError):
    """Indicador possui medições e não pode ser excluído."""

    error_code = "indicator_has_measurements"

    def __init__(self, indicator_id: str) -> None:
        super().__init__(
            f"O indicador com ID '{indicator_id}' possui medições "
            "cadastradas e não pode ser excluído."
        )