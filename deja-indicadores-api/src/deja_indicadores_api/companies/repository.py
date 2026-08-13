from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)


class CompanyRepository:
    """Acesso persistente às empresas cadastradas."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[CompanyModel]:
        """Lista empresas dentro dos filtros institucionais informados."""

        statement = (
            select(CompanyModel)
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
        )

        if organization_id is not None:
            statement = statement.where(
                TenantModel.organization_id == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                TenantModel.id == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                EnvironmentModel.id == environment_id
            )

        statement = statement.order_by(CompanyModel.trade_name)
        return list(self._session.scalars(statement).all())

    def find_by_id(self, company_id: str) -> CompanyModel | None:
        """Localiza uma empresa pelo identificador."""

        return self._session.get(CompanyModel, company_id)

    def find_by_document(self, document: str) -> CompanyModel | None:
        """Localiza uma empresa pelo documento normalizado."""

        statement = select(CompanyModel).where(CompanyModel.document == document)
        return self._session.scalar(statement)

    def add(self, company: CompanyModel) -> CompanyModel:
        """Adiciona e persiste uma empresa."""

        self._session.add(company)
        self._session.commit()
        self._session.refresh(company)
        return company

    def update(self, company: CompanyModel) -> CompanyModel:
        """Persiste as alterações realizadas em uma empresa."""

        self._session.commit()
        self._session.refresh(company)
        return company

    def delete(self, company: CompanyModel) -> None:
        """Remove uma empresa persistentemente."""

        self._session.delete(company)
        self._session.commit()
