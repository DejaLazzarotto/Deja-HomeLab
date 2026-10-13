"""Testes das regras de autorização do serviço de Favoritos."""

from unittest.mock import Mock

import pytest

from deja_indicadores_api.authentication.exceptions import (
    AuthorizationError,
)
from deja_indicadores_api.fotos.media.favorite_service import (
    FotosMediaFavoriteService,
)


@pytest.fixture()
def favorite_service_context():
    """Cria colaboradores simulados sem acessar o banco."""

    repository = Mock()
    media_service = Mock()
    authorization_service = Mock()

    service = FotosMediaFavoriteService(
        repository,
        media_service,
        authorization_service,
    )

    return (
        service,
        repository,
        media_service,
        authorization_service,
    )


@pytest.mark.parametrize(
    "operation",
    [
        "is_favorite",
        "add",
        "remove",
        "list",
    ],
)
def test_favorite_service_blocks_unauthorized_user(
    favorite_service_context,
    operation,
) -> None:
    """Nenhuma operação prossegue quando a autorização é negada."""

    (
        service,
        repository,
        media_service,
        authorization_service,
    ) = favorite_service_context

    current_user = Mock()
    current_user.id = "usuario-sem-permissao"

    authorization_service.require_module_roles.side_effect = (
        AuthorizationError()
    )

    with pytest.raises(AuthorizationError):
        if operation == "list":
            service.list(current_user)
        else:
            getattr(service, operation)(
                "media-nao-autorizada",
                current_user,
            )

    repository.assert_not_called()
    media_service.find_by_id.assert_not_called()

    authorization_service.require_module_roles.assert_called_once()

def test_favorite_service_rejects_cross_organization(
    client,
    test_settings,
    test_session_factory,
) -> None:
    """Impede favoritar mídia de outra organização."""

    from deja_indicadores_api.authentication.authorization import (
        AuthorizationService,
    )
    from deja_indicadores_api.authentication.schemas import (
        AuthenticatedModuleAccess,
        AuthenticatedUser,
    )
    from deja_indicadores_api.fotos.media.dependencies import (
        get_fotos_media_service,
    )
    from deja_indicadores_api.fotos.media.favorite_repository import (
        FotosMediaFavoriteRepository,
    )
    from deja_indicadores_api.user_management.models import (
        UserModuleRole,
        UserRole,
    )
    from tests.authentication.test_authentication_api import (
        create_environment,
        create_organization,
        create_tenant,
        create_user,
    )
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )
    from tests.fotos.media.test_media_api import upload_image
    from tests.module_management.test_authenticated_modules_api import (
        configure_organization_modules,
    )

    organization = create_organization(client)
    organization_id = str(organization["id"])

    configure_organization_modules(
        client,
        organization_id,
        {"fotos"},
    )

    tenant = create_tenant(client, organization_id)
    environment = create_environment(client, str(tenant["id"]))

    administrator = create_user(
        client,
        None,
        email="admin.cross.favorite@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = upload_image(
        client,
        environment_id=str(environment["id"]),
        album_id=None,
        headers=headers,
    )

    assert response.status_code == 201

    media_id = str(response.json()["id"])

    other_organization = create_organization(
        client,
        name="Outra organização Favoritos",
    )

    other_user = create_user(
        client,
        str(other_organization["id"]),
        email="outro.usuario.favorite@deja.com",
        role="organization_admin",
        module_access={"fotos": "manager"},
    )

    current_user = AuthenticatedUser(
        id=str(other_user["id"]),
        organization_id=str(other_organization["id"]),
        tenant_id=None,
        environment_id=None,
        name=str(other_user["name"]),
        email=str(other_user["email"]),
        role=UserRole.ORGANIZATION_ADMIN,
        enabled_modules=["fotos"],
        module_access=[
            AuthenticatedModuleAccess(
                module_key="fotos",
                role=UserModuleRole.MANAGER,
            )
        ],
    )

    with test_session_factory() as session:
        from deja_indicadores_api.fotos.media.dependencies import (
            get_fotos_media_service,
        )

        media_service = get_fotos_media_service(
            session,
            test_settings,
        )

        repository = FotosMediaFavoriteRepository(session)

        service = FotosMediaFavoriteService(
            repository,
            media_service,
            AuthorizationService(),
        )

        with pytest.raises(AuthorizationError):
            service.add(media_id, current_user)

        assert not repository.exists(
            current_user.id,
            media_id,
        )

def test_favorite_service_list_rejects_unauthorized_scope(
    favorite_service_context,
) -> None:
    """Não consulta favoritos quando o escopo solicitado é negado."""

    (
        service,
        repository,
        media_service,
        authorization_service,
    ) = favorite_service_context

    current_user = Mock()
    current_user.id = "usuario-autenticado"

    authorization_service.resolve_list_scope.side_effect = (
        AuthorizationError()
    )

    with pytest.raises(AuthorizationError):
        service.list(
            current_user,
            organization_id="organizacao-nao-autorizada",
        )

    authorization_service.require_module_roles.assert_called_once()

    authorization_service.resolve_list_scope.assert_called_once_with(
        current_user,
        organization_id="organizacao-nao-autorizada",
        tenant_id=None,
        environment_id=None,
    )

    repository.list.assert_not_called()
    media_service.find_by_id.assert_not_called()

def test_favorite_service_list_uses_authenticated_user(
    favorite_service_context,
) -> None:
    """Utiliza a identidade autenticada e o escopo autorizado."""

    (
        service,
        repository,
        _media_service,
        authorization_service,
    ) = favorite_service_context

    current_user = Mock()
    current_user.id = "usuario-autenticado"

    authorization_service.resolve_list_scope.return_value = (
        "organizacao-autorizada",
        "tenant-autorizado",
        "ambiente-autorizado",
    )

    repository.list.return_value = ([], 0)

    items, total = service.list(
        current_user,
        page=2,
        page_size=30,
    )

    assert items == []
    assert total == 0

    repository.list.assert_called_once_with(
        "usuario-autenticado",
        organization_id="organizacao-autorizada",
        tenant_id="tenant-autorizado",
        environment_id="ambiente-autorizado",
        page=2,
        page_size=30,
    )