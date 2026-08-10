from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.models import CompanyModel


class CompanyRepository:
    """Acesso persistente às empresas cadastradas."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[CompanyModel]:
        """Lista as empresas ordenadas pelo nome fantasia."""

        statement = select(CompanyModel).order_by(CompanyModel.trade_name)
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
