from collections.abc import Collection

from sqlalchemy import and_, delete, exists, select
from sqlalchemy.orm import Session

from deja_indicadores_api.module_management.models import (
    ModuleModel,
    OrganizationModuleModel,
)


class ModuleRepository:
    """Acesso persistente ao catálogo de módulos instalados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[ModuleModel]:
        """Lista o catálogo na ordem definida para apresentação."""

        statement = select(ModuleModel).order_by(
            ModuleModel.display_order,
            ModuleModel.name,
        )
        return list(self._session.scalars(statement).all())

    def find_by_key(self, module_key: str) -> ModuleModel | None:
        """Localiza um módulo por sua chave técnica."""

        return self._session.get(ModuleModel, module_key)


class OrganizationModuleRepository:
    """Acesso às liberações de módulos das organizações."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[tuple[ModuleModel, bool]]:
        """Lista o catálogo com o estado aplicado à organização."""

        statement = (
            select(
                ModuleModel,
                OrganizationModuleModel.enabled,
            )
            .outerjoin(
                OrganizationModuleModel,
                and_(
                    OrganizationModuleModel.module_key
                    == ModuleModel.key,
                    OrganizationModuleModel.organization_id
                    == organization_id,
                ),
            )
            .order_by(
                ModuleModel.display_order,
                ModuleModel.name,
            )
        )

        return [
            (
                module,
                bool(enabled)
                if enabled is not None
                else False,
            )
            for module, enabled in self._session.execute(
                statement
            ).all()
        ]

    def list_enabled_module_keys(
        self,
        organization_id: str,
    ) -> list[str]:
        """Lista somente as chaves liberadas para a organização."""

        statement = (
            select(OrganizationModuleModel.module_key)
            .where(
                OrganizationModuleModel.organization_id
                == organization_id,
                OrganizationModuleModel.enabled.is_(True),
            )
            .order_by(OrganizationModuleModel.module_key)
        )
        return list(self._session.scalars(statement).all())

    def is_enabled(
        self,
        organization_id: str,
        module_key: str,
    ) -> bool:
        """Verifica se uma organização possui um módulo liberado."""

        statement = select(
            exists().where(
                OrganizationModuleModel.organization_id
                == organization_id,
                OrganizationModuleModel.module_key == module_key,
                OrganizationModuleModel.enabled.is_(True),
            )
        )
        return bool(self._session.scalar(statement))

    def replace(
        self,
        organization_id: str,
        catalog_keys: Collection[str],
        enabled_keys: Collection[str],
    ) -> None:
        """Substitui atomicamente os estados dos módulos da organização."""

        enabled_key_set = set(enabled_keys)

        try:
            self._session.execute(
                delete(OrganizationModuleModel).where(
                    OrganizationModuleModel.organization_id
                    == organization_id
                )
            )
            self._session.add_all(
                [
                    OrganizationModuleModel(
                        organization_id=organization_id,
                        module_key=module_key,
                        enabled=module_key in enabled_key_set,
                    )
                    for module_key in catalog_keys
                ]
            )
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise