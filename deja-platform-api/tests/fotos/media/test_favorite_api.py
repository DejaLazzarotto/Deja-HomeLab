"""Testes HTTP dos favoritos individuais do Deja Fotos."""

from fastapi.testclient import TestClient

from deja_platform_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_organization,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)

pytest_plugins = (
    "tests.fotos.media.test_favorite_repository",
)
FAVORITES_URL = "/api/fotos/favorites"


def test_list_favorites_starts_empty_for_authenticated_viewer(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Usuário com acesso ao Fotos inicia com lista vazia."""

    organization = create_organization(client)

    user = create_user(
        client,
        str(organization["id"]),
        email="viewer.favoritos.api@deja.com",
        module_access={"fotos": "viewer"},
    )

    headers = authorization_headers(
        test_settings,
        user,
    )

    response = client.get(
        FAVORITES_URL,
        headers=headers,
    )

    assert response.status_code == 200, response.text

    payload = response.json()

    assert payload["items"] == []
    assert payload["total"] == 0
    assert payload["page"] == 1
    assert payload["page_size"] == 30
    assert payload["total_pages"] == 0

def test_favorite_http_full_cycle(
    client: TestClient,
    test_settings: Settings,
    favorite_media_context,
) -> None:
    """Valida inclusão, consulta, listagem e remoção de favorito."""

    from tests.authentication.test_authentication_api import create_user

    context = favorite_media_context
    media_id = context["media_id"]

    # Utiliza o usuário real criado pela fixture institucional.
    user = create_user(
        client,
        None,
        email="administrador.ciclo.favoritos@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(test_settings, user)
    media_url = f"{FAVORITES_URL}/{media_id}"

    initial = client.get(media_url, headers=headers)
    assert initial.status_code == 200, initial.text
    assert initial.json()["is_favorite"] is False

    added = client.put(media_url, headers=headers)
    assert added.status_code == 200, added.text
    assert added.json()["is_favorite"] is True

    status = client.get(media_url, headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["is_favorite"] is True

    # Uma segunda inclusão não deve criar duplicação.
    repeated = client.put(media_url, headers=headers)
    assert repeated.status_code == 200, repeated.text

    listing = client.get(FAVORITES_URL, headers=headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] == 1
    assert len(listing.json()["items"]) == 1
    assert listing.json()["items"][0]["id"] == media_id

    removed = client.delete(media_url, headers=headers)
    assert removed.status_code == 204, removed.text

    final = client.get(media_url, headers=headers)
    assert final.status_code == 200, final.text
    assert final.json()["is_favorite"] is False

    empty = client.get(FAVORITES_URL, headers=headers)
    assert empty.status_code == 200, empty.text
    assert empty.json()["total"] == 0

def test_favorite_http_isolates_users(
    client: TestClient,
    test_settings: Settings,
    favorite_media_context,
) -> None:
    """Favoritos de um usuário não aparecem na conta de outro."""

    from tests.authentication.test_authentication_api import create_user

    context = favorite_media_context
    media_id = context["media_id"]
    media_url = f"{FAVORITES_URL}/{media_id}"

    # Os usuários pertencem à mesma organização, mas têm contas distintas.
    # Recuperamos seus dados reais pelo identificador criado na fixture.
    user1 = create_user(
        client,
        None,
        email="isolamento.favoritos.usuario1@deja.com",
        role="platform_admin",
    )
    user2 = create_user(
        client,
        None,
        email="isolamento.favoritos.usuario2@deja.com",
        role="platform_admin",
    )

    headers1 = authorization_headers(test_settings, user1)
    headers2 = authorization_headers(test_settings, user2)

    added = client.put(media_url, headers=headers1)
    assert added.status_code == 200, added.text

    own_status = client.get(media_url, headers=headers1)
    assert own_status.status_code == 200, own_status.text
    assert own_status.json()["is_favorite"] is True

    other_status = client.get(media_url, headers=headers2)
    assert other_status.status_code == 200, other_status.text
    assert other_status.json()["is_favorite"] is False

    own_list = client.get(FAVORITES_URL, headers=headers1)
    assert own_list.status_code == 200, own_list.text
    assert own_list.json()["total"] == 1

    other_list = client.get(FAVORITES_URL, headers=headers2)
    assert other_list.status_code == 200, other_list.text
    assert other_list.json()["total"] == 0

    # A remoção feita pela segunda conta não altera o favorito da primeira.
    removed_by_other = client.delete(media_url, headers=headers2)
    assert removed_by_other.status_code == 204, removed_by_other.text

    still_favorite = client.get(media_url, headers=headers1)
    assert still_favorite.status_code == 200, still_favorite.text
    assert still_favorite.json()["is_favorite"] is True

def test_favorite_http_rejects_other_organization(
    client: TestClient,
    test_settings: Settings,
    favorite_media_context,
) -> None:
    """Viewer não acessa favoritos de mídias de outra organização."""

    from tests.module_management.test_authenticated_modules_api import (
        configure_organization_modules,
    )

    context = favorite_media_context
    media_id = context["media_id"]
    media_url = f"{FAVORITES_URL}/{media_id}"

    other_organization = create_organization(
        client,
        name="Organização Secundária Favoritos",
    )
    other_organization_id = str(other_organization["id"])

    configure_organization_modules(
        client,
        other_organization_id,
        {"fotos"},
    )

    other_user = create_user(
        client,
        other_organization_id,
        email="viewer.outra.organizacao.favoritos@deja.com",
        module_access={"fotos": "viewer"},
    )

    headers = authorization_headers(test_settings, other_user)

    for method in ("GET", "PUT", "DELETE"):
        response = client.request(
            method,
            media_url,
            headers=headers,
        )
        assert response.status_code in (403, 404), (
            method,
            response.status_code,
            response.text,
        )

    listing = client.get(FAVORITES_URL, headers=headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["items"] == []
    assert listing.json()["total"] == 0

def test_favorite_http_isolates_viewers(
    client: TestClient,
    test_settings: Settings,
    favorite_media_context,
) -> None:
    """Dois viewers da mesma organização têm favoritos independentes."""

    from deja_platform_api.user_management.models import UserModel

    context = favorite_media_context
    media_id = context["media_id"]
    media_url = f"{FAVORITES_URL}/{media_id}"

    with context["session_factory"]() as session:
        user1 = session.get(UserModel, context["user1"])
        user2 = session.get(UserModel, context["user2"])

        assert user1 is not None
        assert user2 is not None

        user1_data = {
            "id": user1.id,
            "organization_id": user1.organization_id,
            "tenant_id": user1.tenant_id,
            "environment_id": user1.environment_id,
            "email": user1.email,
            "role": user1.role.value,
        }
        user2_data = {
            "id": user2.id,
            "organization_id": user2.organization_id,
            "tenant_id": user2.tenant_id,
            "environment_id": user2.environment_id,
            "email": user2.email,
            "role": user2.role.value,
        }
    headers1 = authorization_headers(test_settings, user1_data)
    headers2 = authorization_headers(test_settings, user2_data)

    added = client.put(media_url, headers=headers1)
    assert added.status_code == 200, added.text

    own_list = client.get(FAVORITES_URL, headers=headers1)
    assert own_list.status_code == 200, own_list.text
    assert own_list.json()["total"] == 1

    other_list = client.get(FAVORITES_URL, headers=headers2)
    assert other_list.status_code == 200, other_list.text
    assert other_list.json()["total"] == 0

    other_status = client.get(media_url, headers=headers2)
    assert other_status.status_code == 200, other_status.text
    assert other_status.json()["is_favorite"] is False