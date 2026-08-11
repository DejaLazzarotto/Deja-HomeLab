from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.user_management.models import (
    UserModel,
    UserStatus,
)


class UserRepository:
    """Acesso persistente aos usuários cadastrados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        status: UserStatus | None = None,
    ) -> list[UserModel]:
        """Lista usuários ordenados pelo nome e com filtros opcionais."""

        statement = select(UserModel)

        if organization_id is not None:
            statement = statement.where(
                UserModel.organization_id == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                UserModel.tenant_id == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                UserModel.environment_id == environment_id
            )

        if status is not None:
            statement = statement.where(UserModel.status == status)

        statement = statement.order_by(UserModel.name, UserModel.email)

        return list(self._session.scalars(statement).all())

    def find_by_id(self, user_id: str) -> UserModel | None:
        """Localiza um usuário pelo identificador."""

        return self._session.get(UserModel, user_id)

    def find_by_organization_and_email(
        self,
        organization_id: str,
        email: str,
    ) -> UserModel | None:
        """Localiza um usuário pelo e-mail dentro da organização."""

        statement = select(UserModel).where(
            UserModel.organization_id == organization_id,
            UserModel.email == email,
        )
        return self._session.scalar(statement)

    def add(self, user: UserModel) -> UserModel:
        """Adiciona e persiste um usuário."""

        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def update(self, user: UserModel) -> UserModel:
        """Persiste as alterações realizadas em um usuário."""

        self._session.commit()
        self._session.refresh(user)
        return user