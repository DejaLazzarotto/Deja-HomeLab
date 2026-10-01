from collections.abc import Collection

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from deja_indicadores_api.user_management.models import (
    UserModel,
    UserModuleAccessModel,
    UserModuleRole,
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
            statement = statement.where(
                UserModel.status == status
            )

        statement = statement.order_by(
            UserModel.name,
            UserModel.email,
        )

        return list(
            self._session.scalars(statement).all()
        )

    def find_by_id(
        self,
        user_id: str,
    ) -> UserModel | None:
        """Localiza um usuário pelo identificador."""

        return self._session.get(
            UserModel,
            user_id,
        )

    def find_by_organization_and_email(
        self,
        organization_id: str | None,
        email: str,
    ) -> UserModel | None:
        """Localiza um usuário pelo e-mail dentro do seu escopo."""

        statement = select(UserModel).where(
            UserModel.organization_id == organization_id,
            UserModel.email == email,
        )

        return self._session.scalar(statement)

    def add(
        self,
        user: UserModel,
    ) -> UserModel:
        """Adiciona e persiste um usuário."""

        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)

        return user

    def update(
        self,
        user: UserModel,
    ) -> UserModel:
        """Persiste as alterações realizadas em um usuário."""

        self._session.commit()
        self._session.refresh(user)

        return user


class UserModuleAccessRepository:
    """Acesso persistente aos módulos liberados para usuários."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def list_for_user(
        self,
        user_id: str,
    ) -> list[UserModuleAccessModel]:
        """Lista os acessos de módulo do usuário."""

        statement = (
            select(UserModuleAccessModel)
            .where(
                UserModuleAccessModel.user_id == user_id
            )
            .order_by(
                UserModuleAccessModel.module_key
            )
        )

        return list(
            self._session.scalars(statement).all()
        )

    def find(
        self,
        user_id: str,
        module_key: str,
    ) -> UserModuleAccessModel | None:
        """Localiza um acesso específico do usuário."""

        return self._session.get(
            UserModuleAccessModel,
            (user_id, module_key),
        )

    def replace(
        self,
        user_id: str,
        accesses: Collection[
            tuple[str, UserModuleRole]
        ],
    ) -> None:
        """Substitui integralmente os acessos do usuário."""

        try:
            self._session.execute(
                delete(UserModuleAccessModel).where(
                    UserModuleAccessModel.user_id
                    == user_id
                )
            )

            self._session.add_all(
                [
                    UserModuleAccessModel(
                        user_id=user_id,
                        module_key=module_key,
                        role=role,
                    )
                    for module_key, role in accesses
                ]
            )

            self._session.commit()
        except Exception:
            self._session.rollback()
            raise