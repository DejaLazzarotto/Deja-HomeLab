from uuid import uuid4

from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
    OrganizationHasTenantsError,
    OrganizationNameAlreadyExistsError,
    OrganizationNotFoundError,
    TenantHasEnvironmentsError,
    TenantNameAlreadyExistsError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    OrganizationRepository,
    TenantRepository,
)
from deja_indicadores_api.tenant_management.schemas import (
    EnvironmentCreate,
    EnvironmentUpdate,
    OrganizationCreate,
    OrganizationUpdate,
    TenantCreate,
    TenantUpdate,
)


class OrganizationService:
    """Regras de aplicação para organizações."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository

    def list(self) -> list[OrganizationModel]:
        """Lista todas as organizações cadastradas."""

        return self._organization_repository.list()

    def find_by_id(self, organization_id: str) -> OrganizationModel:
        """Retorna uma organização pelo identificador."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)

        return organization

    def create(
        self,
        input_data: OrganizationCreate,
    ) -> OrganizationModel:
        """Cadastra uma nova organização."""

        existing_organization = (
            self._organization_repository.find_by_name(input_data.name)
        )

        if existing_organization is not None:
            raise OrganizationNameAlreadyExistsError(input_data.name)

        organization = OrganizationModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._organization_repository.add(organization)

    def update(
        self,
        organization_id: str,
        input_data: OrganizationUpdate,
    ) -> OrganizationModel:
        """Atualiza integralmente uma organização existente."""

        organization = self.find_by_id(organization_id)
        name_owner = self._organization_repository.find_by_name(
            input_data.name
        )

        if (
            name_owner is not None
            and name_owner.id != organization_id
        ):
            raise OrganizationNameAlreadyExistsError(input_data.name)

        for field_name, value in input_data.model_dump().items():
            setattr(organization, field_name, value)

        return self._organization_repository.update(organization)

    def delete(self, organization_id: str) -> None:
        """Exclui uma organização que não possua tenants."""

        organization = self.find_by_id(organization_id)

        if self._tenant_repository.exists_for_organization(
            organization_id
        ):
            raise OrganizationHasTenantsError(organization_id)

        self._organization_repository.delete(organization)


class TenantService:
    """Regras de aplicação para tenants."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository

    def list(self) -> list[TenantModel]:
        """Lista todos os tenants cadastrados."""

        return self._tenant_repository.list()

    def find_by_id(self, tenant_id: str) -> TenantModel:
        """Retorna um tenant pelo identificador."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def create(self, input_data: TenantCreate) -> TenantModel:
        """Cadastra um novo tenant."""

        self._require_organization(input_data.organization_id)

        existing_tenant = (
            self._tenant_repository.find_by_organization_and_name(
                input_data.organization_id,
                input_data.name,
            )
        )

        if existing_tenant is not None:
            raise TenantNameAlreadyExistsError(
                input_data.organization_id,
                input_data.name,
            )

        tenant = TenantModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._tenant_repository.add(tenant)

    def update(
        self,
        tenant_id: str,
        input_data: TenantUpdate,
    ) -> TenantModel:
        """Atualiza integralmente um tenant existente."""

        tenant = self.find_by_id(tenant_id)
        self._require_organization(input_data.organization_id)

        name_owner = (
            self._tenant_repository.find_by_organization_and_name(
                input_data.organization_id,
                input_data.name,
            )
        )

        if name_owner is not None and name_owner.id != tenant_id:
            raise TenantNameAlreadyExistsError(
                input_data.organization_id,
                input_data.name,
            )

        for field_name, value in input_data.model_dump().items():
            setattr(tenant, field_name, value)

        return self._tenant_repository.update(tenant)

    def delete(self, tenant_id: str) -> None:
        """Exclui um tenant que não possua ambientes."""

        tenant = self.find_by_id(tenant_id)

        if self._environment_repository.exists_for_tenant(tenant_id):
            raise TenantHasEnvironmentsError(tenant_id)

        self._tenant_repository.delete(tenant)

    def _require_organization(
        self,
        organization_id: str,
    ) -> OrganizationModel:
        """Garante que a organização informada exista."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)

        return organization


class EnvironmentService:
    """Regras de aplicação para ambientes."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository

    def list(self) -> list[EnvironmentModel]:
        """Lista todos os ambientes cadastrados."""

        return self._environment_repository.list()

    def find_by_id(self, environment_id: str) -> EnvironmentModel:
        """Retorna um ambiente pelo identificador."""

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        return environment

    def create(
        self,
        input_data: EnvironmentCreate,
    ) -> EnvironmentModel:
        """Cadastra um novo ambiente."""

        self._require_tenant(input_data.tenant_id)

        existing_environment = (
            self._environment_repository.find_by_tenant_and_name(
                input_data.tenant_id,
                input_data.name,
            )
        )

        if existing_environment is not None:
            raise EnvironmentNameAlreadyExistsError(
                input_data.tenant_id,
                input_data.name,
            )

        environment = EnvironmentModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._environment_repository.add(environment)

    def update(
        self,
        environment_id: str,
        input_data: EnvironmentUpdate,
    ) -> EnvironmentModel:
        """Atualiza integralmente um ambiente existente."""

        environment = self.find_by_id(environment_id)
        self._require_tenant(input_data.tenant_id)

        name_owner = (
            self._environment_repository.find_by_tenant_and_name(
                input_data.tenant_id,
                input_data.name,
            )
        )

        if (
            name_owner is not None
            and name_owner.id != environment_id
        ):
            raise EnvironmentNameAlreadyExistsError(
                input_data.tenant_id,
                input_data.name,
            )

        for field_name, value in input_data.model_dump().items():
            setattr(environment, field_name, value)

        return self._environment_repository.update(environment)

    def delete(self, environment_id: str) -> None:
        """Exclui um ambiente."""

        environment = self.find_by_id(environment_id)
        self._environment_repository.delete(environment)

    def _require_tenant(self, tenant_id: str) -> TenantModel:
        """Garante que o tenant informado exista."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant