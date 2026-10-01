from deja_indicadores_api.core.exceptions import (
    ApplicationError,
    ResourceConflictError,
    ResourceNotFoundError,
)


class UserNotFoundError(ResourceNotFoundError):
    """Usuário solicitado não encontrado."""

    error_code = "user_not_found"

    def __init__(self, user_id: str) -> None:
        super().__init__(
            f"Usuário com ID '{user_id}' não encontrado."
        )


class UserEmailAlreadyExistsError(ResourceConflictError):
    """E-mail já utilizado por outro usuário no mesmo escopo."""

    error_code = "user_email_already_exists"

    def __init__(
        self,
        organization_id: str | None,
        email: str,
    ) -> None:
        if organization_id is None:
            message = (
                "A plataforma já possui um administrador global "
                f"com o e-mail '{email}'."
            )
        else:
            message = (
                f"A organização com ID '{organization_id}' já possui "
                f"um usuário com o e-mail '{email}'."
            )

        super().__init__(message)


class TenantDoesNotBelongToOrganizationError(ApplicationError):
    """Tenant informado não pertence à organização do usuário."""

    error_code = "tenant_does_not_belong_to_organization"

    def __init__(
        self,
        tenant_id: str,
        organization_id: str,
    ) -> None:
        super().__init__(
            f"O tenant com ID '{tenant_id}' não pertence à "
            f"organização com ID '{organization_id}'."
        )


class EnvironmentRequiresTenantError(ApplicationError):
    """Ambiente não pode ser informado sem um tenant."""

    error_code = "environment_requires_tenant"

    def __init__(self, environment_id: str) -> None:
        super().__init__(
            f"O ambiente com ID '{environment_id}' exige que um "
            "tenant também seja informado."
        )


class EnvironmentDoesNotBelongToTenantError(ApplicationError):
    """Ambiente informado não pertence ao tenant do usuário."""

    error_code = "environment_does_not_belong_to_tenant"

    def __init__(
        self,
        environment_id: str,
        tenant_id: str,
    ) -> None:
        super().__init__(
            f"O ambiente com ID '{environment_id}' não pertence "
            f"ao tenant com ID '{tenant_id}'."
        )


class RoleScopeMismatchError(ApplicationError):
    """Papel informado é incompatível com o escopo institucional."""

    error_code = "role_scope_mismatch"

    def __init__(self, role: str, reason: str) -> None:
        super().__init__(
            f"O papel '{role}' é incompatível com o escopo informado: "
            f"{reason}."
        )


class UserModuleAccessNotApplicableError(ApplicationError):
    """Usuário não admite acessos funcionais por módulo."""

    error_code = "user_module_access_not_applicable"

    def __init__(self, role: str) -> None:
        super().__init__(
            f"O papel institucional '{role}' não utiliza "
            "acessos funcionais por módulo."
        )


class UserModuleNotEnabledForOrganizationError(ApplicationError):
    """Módulo solicitado não está liberado para a organização."""

    error_code = "user_module_not_enabled_for_organization"

    def __init__(
        self,
        organization_id: str,
        module_key: str,
    ) -> None:
        super().__init__(
            f"O módulo '{module_key}' não está habilitado para "
            f"a organização com ID '{organization_id}'."
        )