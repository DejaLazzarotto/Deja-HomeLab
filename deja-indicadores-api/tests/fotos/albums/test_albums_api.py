from collections.abc import Mapping
from io import BytesIO
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)

ALBUMS_URL = "/api/fotos/albums"

FIRST_ALBUM = {
    "name": " Família ",
    "description": " Álbum principal da família. ",
    "active": True,
}

SECOND_ALBUM = {
    "name": "Viagens",
    "description": "Registros de viagens.",
    "active": False,
}


@pytest.fixture()
def album_context(
    client: TestClient,
    test_settings: Settings,
) -> tuple[str, str, str, Mapping[str, str]]:
    """Cria a hierarquia institucional para os testes do Deja Fotos."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    administrator = create_user(
        client,
        None,
        email="platform.admin.fotos.albums@deja.com",
        role="platform_admin",
    )

    return (
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
        authorization_headers(
            test_settings,
            administrator,
        ),
    )


def album_payload(
    payload: dict[str, object],
    environment_id: str,
) -> dict[str, object]:
    """Adiciona o ambiente institucional ao contrato do álbum."""

    return {
        "environment_id": environment_id,
        **payload,
    }


def create_album(
    client: TestClient,
    payload: dict[str, object],
    environment_id: str,
    headers: Mapping[str, str],
) -> dict[str, object]:
    """Cadastra um álbum e retorna o corpo da resposta."""

    response = client.post(
        ALBUMS_URL,
        json=album_payload(
            payload,
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 201
    return response.json()


def test_create_album_normalizes_and_derives_scope(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Cria álbum normalizando os textos e derivando o escopo."""

    (
        organization_id,
        tenant_id,
        environment_id,
        headers,
    ) = album_context

    response = client.post(
        ALBUMS_URL,
        json=album_payload(
            FIRST_ALBUM,
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["organization_id"] == organization_id
    assert body["tenant_id"] == tenant_id
    assert body["environment_id"] == environment_id
    assert body["name"] == "Família"
    assert body["description"] == "Álbum principal da família."
    assert body["active"] is True
    assert body["created_at"]
    assert body["updated_at"]


def test_list_albums_filters_by_active(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista álbuns filtrando pela situação."""

    _, _, environment_id, headers = album_context

    create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )
    second_album = create_album(
        client,
        SECOND_ALBUM,
        environment_id,
        headers,
    )

    response = client.get(
        ALBUMS_URL,
        params={
            "active": "false",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert [
        album["id"]
        for album in response.json()
    ] == [
        second_album["id"],
    ]


def test_list_albums_returns_name_order(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista álbuns em ordem alfabética pelo nome."""

    _, _, environment_id, headers = album_context

    create_album(
        client,
        SECOND_ALBUM,
        environment_id,
        headers,
    )
    create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    response = client.get(
        ALBUMS_URL,
        headers=headers,
    )

    assert response.status_code == 200
    assert [
        album["name"]
        for album in response.json()
    ] == [
        "Família",
        "Viagens",
    ]


def test_get_album_by_id(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Consulta um álbum pelo identificador."""

    _, _, environment_id, headers = album_context

    created_album = create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    response = client.get(
        f"{ALBUMS_URL}/{created_album['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == created_album


def test_update_album(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Atualiza integralmente um álbum."""

    _, _, environment_id, headers = album_context

    created_album = create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    response = client.put(
        f"{ALBUMS_URL}/{created_album['id']}",
        json=album_payload(
            {
                "name": "Família Atualizada",
                "description": "Nova descrição.",
                "active": False,
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created_album["id"]
    assert body["name"] == "Família Atualizada"
    assert body["description"] == "Nova descrição."
    assert body["active"] is False
    assert body["environment_id"] == environment_id


def test_delete_album(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Exclui um álbum vazio."""

    _, _, environment_id, headers = album_context

    created_album = create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    delete_response = client.delete(
        f"{ALBUMS_URL}/{created_album['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"{ALBUMS_URL}/{created_album['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert (
        get_response.json()["error"]
        == "fotos_album_not_found"
    )


def test_create_album_rejects_duplicate_name_in_same_scope(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita nome repetido dentro do mesmo ambiente."""

    _, _, environment_id, headers = album_context

    create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    response = client.post(
        ALBUMS_URL,
        json=album_payload(
            {
                **FIRST_ALBUM,
                "description": "Outra descrição.",
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 409
    assert (
        response.json()["error"]
        == "fotos_album_already_exists"
    )


def test_same_album_name_is_allowed_in_different_scopes(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite o mesmo nome em organizações diferentes."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Fotos Secundária",
    )

    first_tenant = create_tenant(
        client,
        str(first_organization["id"]),
    )
    second_tenant = create_tenant(
        client,
        str(second_organization["id"]),
    )

    first_environment = create_environment(
        client,
        str(first_tenant["id"]),
    )
    second_environment = create_environment(
        client,
        str(second_tenant["id"]),
    )

    administrator = create_user(
        client,
        None,
        email="platform.admin.fotos.scopes@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    first_response = client.post(
        ALBUMS_URL,
        json=album_payload(
            FIRST_ALBUM,
            str(first_environment["id"]),
        ),
        headers=headers,
    )

    second_response = client.post(
        ALBUMS_URL,
        json=album_payload(
            FIRST_ALBUM,
            str(second_environment["id"]),
        ),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert (
        first_response.json()["organization_id"]
        != second_response.json()["organization_id"]
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("name", ""),
        ("environment_id", "invalid-id"),
    ],
)
def test_create_album_rejects_invalid_data(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
    field_name: str,
    invalid_value: str,
) -> None:
    """Rejeita dados inválidos no cadastro."""

    _, _, environment_id, headers = album_context

    payload = album_payload(
        FIRST_ALBUM,
        environment_id,
    )
    payload[field_name] = invalid_value

    response = client.post(
        ALBUMS_URL,
        json=payload,
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "put",
        "delete",
    ],
)
def test_unknown_album_returns_not_found(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
    method: str,
) -> None:
    """Retorna 404 nas operações sobre álbum inexistente."""

    _, _, environment_id, headers = album_context

    album_id = str(uuid4())
    request = getattr(client, method)

    request_arguments: dict[str, object] = {
        "headers": headers,
    }

    if method == "put":
        request_arguments["json"] = album_payload(
            FIRST_ALBUM,
            environment_id,
        )

    response = request(
        f"{ALBUMS_URL}/{album_id}",
        **request_arguments,
    )

    assert response.status_code == 404
    assert (
        response.json()["error"]
        == "fotos_album_not_found"
    )


def test_album_id_requires_36_characters(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    _, _, _, headers = album_context

    response = client.get(
        f"{ALBUMS_URL}/invalid-id",
        headers=headers,
    )

    assert response.status_code == 422

def test_delete_album_with_media_returns_conflict(
    client: TestClient,
    album_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Impede exclusão de álbum com mídia ativa vinculada."""

    _, _, environment_id, headers = album_context

    album = create_album(
        client,
        FIRST_ALBUM,
        environment_id,
        headers,
    )

    buffer = BytesIO()

    Image.new(
        "RGB",
        (16, 12),
    ).save(
        buffer,
        format="JPEG",
    )

    upload_response = client.post(
        "/api/fotos/media",
        data={
            "environment_id": environment_id,
            "album_id": album["id"],
        },
        files={
            "file": (
                "foto.jpg",
                buffer.getvalue(),
                "image/jpeg",
            ),
        },
        headers=headers,
    )

    assert upload_response.status_code == 201

    delete_response = client.delete(
        f"{ALBUMS_URL}/{album['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 409
    assert (
        delete_response.json()["error"]
        == "fotos_album_has_media"
    )

    get_response = client.get(
        f"{ALBUMS_URL}/{album['id']}",
        headers=headers,
    )

    assert get_response.status_code == 200