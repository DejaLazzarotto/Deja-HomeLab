from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)


class OrganizationRepository:
    """Acesso persistente às organizações cadastradas."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[OrganizationModel]:
        """Lista as organizações ordenadas pelo nome."""

        statement = select(OrganizationModel).order_by(
            OrganizationModel.name
        )
        return list(self._session.scalars(statement).all())

    def find_by_id(
        self,
        organization_id: str,
    ) -> OrganizationModel | None:
        """Localiza uma organização pelo identificador."""

        return self._session.get(OrganizationModel, organization_id)

    def find_by_name(
        self,
        name: str,
    ) -> OrganizationModel | None:
        """Localiza uma organização pelo nome."""

        statement = select(OrganizationModel).where(
            OrganizationModel.name == name
        )
        return self._session.scalar(statement)

    def add(
        self,
        organization: OrganizationModel,
    ) -> OrganizationModel:
        """Adiciona e persiste uma organização."""

        self._session.add(organization)
        self._session.commit()
        self._session.refresh(organization)
        return organization

    def update(
        self,
        organization: OrganizationModel,
    ) -> OrganizationModel:
        """Persiste as alterações realizadas em uma organização."""

        self._session.commit()
        self._session.refresh(organization)
        return organization

    def delete(self, organization: OrganizationModel) -> None:
        """Remove uma organização persistentemente."""

        self._session.delete(organization)
        self._session.commit()


class TenantRepository:
    """Acesso persistente aos tenants cadastrados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[TenantModel]:
        """Lista os tenants ordenados pelo nome."""

        statement = select(TenantModel).order_by(TenantModel.name)
        return list(self._session.scalars(statement).all())

    def find_by_id(self, tenant_id: str) -> TenantModel | None:
        """Localiza um tenant pelo identificador."""

        return self._session.get(TenantModel, tenant_id)

    def find_by_organization_and_name(
        self,
        organization_id: str,
        name: str,
    ) -> TenantModel | None:
        """Localiza um tenant pelo nome dentro da organização."""

        statement = select(TenantModel).where(
            TenantModel.organization_id == organization_id,
            TenantModel.name == name,
        )
        return self._session.scalar(statement)

    def exists_for_organization(self, organization_id: str) -> bool:
        """Verifica se a organização possui tenants cadastrados."""

        statement = select(
            exists().where(
                TenantModel.organization_id == organization_id
            )
        )
        return bool(self._session.scalar(statement))

    def add(self, tenant: TenantModel) -> TenantModel:
        """Adiciona e persiste um tenant."""

        self._session.add(tenant)
        self._session.commit()
        self._session.refresh(tenant)
        return tenant

    def update(self, tenant: TenantModel) -> TenantModel:
        """Persiste as alterações realizadas em um tenant."""

        self._session.commit()
        self._session.refresh(tenant)
        return tenant

    def delete(self, tenant: TenantModel) -> None:
        """Remove um tenant persistentemente."""

        self._session.delete(tenant)
        self._session.commit()


class EnvironmentRepository:
    """Acesso persistente aos ambientes cadastrados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[EnvironmentModel]:
        """Lista os ambientes ordenados pelo nome."""

        statement = select(EnvironmentModel).order_by(
            EnvironmentModel.name
        )
        return list(self._session.scalars(statement).all())

    def find_by_id(
        self,
        environment_id: str,
    ) -> EnvironmentModel | None:
        """Localiza um ambiente pelo identificador."""

        return self._session.get(EnvironmentModel, environment_id)

    def find_by_tenant_and_name(
        self,
        tenant_id: str,
        name: str,
    ) -> EnvironmentModel | None:
        """Localiza um ambiente pelo nome dentro do tenant."""

        statement = select(EnvironmentModel).where(
            EnvironmentModel.tenant_id == tenant_id,
            EnvironmentModel.name == name,
        )
        return self._session.scalar(statement)

    def exists_for_tenant(self, tenant_id: str) -> bool:
        """Verifica se o tenant possui ambientes cadastrados."""

        statement = select(
            exists().where(EnvironmentModel.tenant_id == tenant_id)
        )
        return bool(self._session.scalar(statement))

    def add(
        self,
        environment: EnvironmentModel,
    ) -> EnvironmentModel:
        """Adiciona e persiste um ambiente."""

        self._session.add(environment)
        self._session.commit()
        self._session.refresh(environment)
        return environment

    def update(
        self,
        environment: EnvironmentModel,
    ) -> EnvironmentModel:
        """Persiste as alterações realizadas em um ambiente."""

        self._session.commit()
        self._session.refresh(environment)
        return environment

    def delete(self, environment: EnvironmentModel) -> None:
        """Remove um ambiente persistentemente."""

        self._session.delete(environment)
        self._session.commit()