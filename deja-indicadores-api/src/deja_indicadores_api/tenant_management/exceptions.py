from deja_indicadores_api.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


class OrganizationNotFoundError(ResourceNotFoundError):
    """Organização solicitada não encontrada."""

    error_code = "organization_not_found"

    def __init__(self, organization_id: str) -> None:
        super().__init__(f"Organização com ID '{organization_id}' não encontrada.")


class OrganizationCodeAlreadyExistsError(ResourceConflictError):
    """Código já utilizado por outra organização."""

    error_code = "organization_code_already_exists"

    def __init__(self, code: str) -> None:
        super().__init__(f"Já existe uma organização com o código '{code}'.")


class OrganizationNameAlreadyExistsError(ResourceConflictError):
    """Nome já utilizado por outra organização."""

    error_code = "organization_name_already_exists"

    def __init__(self, name: str) -> None:
        super().__init__(f"Já existe uma organização chamada '{name}'.")


class OrganizationHasTenantsError(ResourceConflictError):
    """Organização possui tenants e não pode ser excluída."""

    error_code = "organization_has_tenants"

    def __init__(self, organization_id: str) -> None:
        super().__init__(
            f"A organização com ID '{organization_id}' possui tenants "
            "cadastrados e não pode ser excluída."
        )


class TenantNotFoundError(ResourceNotFoundError):
    """Tenant solicitado não encontrado."""

    error_code = "tenant_not_found"

    def __init__(self, tenant_id: str) -> None:
        super().__init__(f"Tenant com ID '{tenant_id}' não encontrado.")


class TenantNameAlreadyExistsError(ResourceConflictError):
    """Nome de tenant já utilizado dentro da organização."""

    error_code = "tenant_name_already_exists"

    def __init__(self, organization_id: str, name: str) -> None:
        super().__init__(
            f"A organização com ID '{organization_id}' já possui um tenant chamado '{name}'."
        )


class TenantHasEnvironmentsError(ResourceConflictError):
    """Tenant possui ambientes e não pode ser excluído."""

    error_code = "tenant_has_environments"

    def __init__(self, tenant_id: str) -> None:
        super().__init__(
            f"O tenant com ID '{tenant_id}' possui ambientes cadastrados e não pode ser excluído."
        )


class EnvironmentNotFoundError(ResourceNotFoundError):
    """Ambiente solicitado não encontrado."""

    error_code = "environment_not_found"

    def __init__(self, environment_id: str) -> None:
        super().__init__(f"Ambiente com ID '{environment_id}' não encontrado.")


class EnvironmentNameAlreadyExistsError(ResourceConflictError):
    """Nome de ambiente já utilizado dentro do tenant."""

    error_code = "environment_name_already_exists"

    def __init__(self, tenant_id: str, name: str) -> None:
        super().__init__(f"O tenant com ID '{tenant_id}' já possui um ambiente chamado '{name}'.")
