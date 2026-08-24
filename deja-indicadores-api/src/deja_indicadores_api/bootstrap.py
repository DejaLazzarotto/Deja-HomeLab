import sys
from getpass import getpass
from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from deja_indicadores_api.core.database import SessionLocal
from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.module_management.models import (
    ModuleModel,
    OrganizationModuleModel,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
    UserStatus,
)
from deja_indicadores_api.user_management.schemas import (
    UserCreate,
    UserPasswordSet,
)

_registered_models = (
    OrganizationModel,
    TenantModel,
    EnvironmentModel,
    ModuleModel,
    OrganizationModuleModel,
    UserModel,
)


class InitialPlatformAdminAlreadyExistsError(RuntimeError):
    """Indica que o administrador inicial já foi provisionado."""


class PasswordConfirmationMismatchError(ValueError):
    """Indica divergência entre a senha e sua confirmação."""


def create_initial_platform_admin(
    session: Session,
    *,
    name: str,
    email: str,
    password: str,
    password_confirmation: str,
) -> UserModel:
    """Cria o primeiro administrador global da plataforma."""

    if password != password_confirmation:
        raise PasswordConfirmationMismatchError(
            "A senha e a confirmação não coincidem."
        )

    input_data = UserCreate(
        organization_id=None,
        tenant_id=None,
        environment_id=None,
        name=name,
        email=email,
        role=UserRole.PLATFORM_ADMIN,
        status=UserStatus.ACTIVE,
    )
    password_data = UserPasswordSet(password=password)

    existing_administrator_id = session.scalar(
        select(UserModel.id)
        .where(UserModel.role == UserRole.PLATFORM_ADMIN)
        .limit(1)
    )

    if existing_administrator_id is not None:
        raise InitialPlatformAdminAlreadyExistsError(
            "O platform_admin inicial já foi provisionado."
        )

    administrator = UserModel(
        id=str(uuid4()),
        **input_data.model_dump(),
        password_hash=PasswordService().hash(password_data.password),
    )

    try:
        session.add(administrator)
        session.commit()
        session.refresh(administrator)
    except Exception:
        session.rollback()
        raise

    return administrator


def main() -> int:
    """Executa o provisionamento interativo do administrador inicial."""

    print("Provisionamento do primeiro platform_admin")
    name = input("Nome: ")
    email = input("E-mail: ")
    password = getpass("Senha: ")
    password_confirmation = getpass("Confirme a senha: ")

    try:
        with SessionLocal() as session:
            administrator = create_initial_platform_admin(
                session,
                name=name,
                email=email,
                password=password,
                password_confirmation=password_confirmation,
            )
    except InitialPlatformAdminAlreadyExistsError as error:
        print(str(error), file=sys.stderr)
        return 1
    except PasswordConfirmationMismatchError as error:
        print(str(error), file=sys.stderr)
        return 1
    except ValidationError:
        print(
            "Dados inválidos. Verifique nome, e-mail e senha "
            "(entre 8 e 128 caracteres).",
            file=sys.stderr,
        )
        return 1
    except SQLAlchemyError:
        print(
            "Não foi possível persistir o platform_admin no banco de dados.",
            file=sys.stderr,
        )
        return 1

    print(
        "platform_admin criado com sucesso: "
        f"{administrator.name} <{administrator.email}>"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())