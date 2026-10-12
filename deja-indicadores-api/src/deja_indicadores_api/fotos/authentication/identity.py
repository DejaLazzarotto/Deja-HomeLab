"""Identificacao de usuarios para a autenticacao do Fotos PWA."""

from sqlalchemy.orm import Session

from deja_indicadores_api.tenant_management.repository import (
    OrganizationRepository,
)
from deja_indicadores_api.user_management.models import UserModel
from deja_indicadores_api.user_management.repository import UserRepository


class FotosVerificationIdentityService:
    """Localiza contas pelo codigo da organizacao e e-mail."""

    def __init__(self, session: Session) -> None:
        self._organization_repository = OrganizationRepository(session)
        self._user_repository = UserRepository(session)

    def find_user(
        self,
        *,
        organization_code: str,
        email: str,
    ) -> UserModel | None:
        """Identifica o usuario exclusivamente em sua organizacao."""

        organization = self._organization_repository.find_by_code(
            organization_code,
        )

        if organization is None:
            return None

        return self._user_repository.find_by_organization_and_email(
            organization.id,
            email,
        )
