from collections.abc import Mapping
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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
from tests.fotos.albums.test_albums_api import (
    FIRST_ALBUM,
    create_album,
)

MEDIA_URL = "/api/fotos/media"


@pytest.fixture()
def media_context(
    client: TestClient,
    test_settings: Settings,
) -> tuple[
    str,
    str,
    str,
    str,
    Mapping[str, str],
]:
    """Cria o contexto institucional para os testes de mídias."""

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
        email="platform.admin.fotos.media@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    album = create_album(
        client,
        FIRST_ALBUM,
        str(environment["id"]),
        headers,
    )

    return (
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
        str(album["id"]),
        headers,
    )


def upload_image(
    client: TestClient,
    *,
    environment_id: str,
    album_id: str | None,
    headers: Mapping[str, str],
    file_name: str = "foto.jpg",
    content: bytes = b"conteudo-da-foto",
    content_type: str = "image/jpeg",
):
    """Envia uma mídia de teste."""

    data = {
        "environment_id": environment_id,
    }

    if album_id is not None:
        data["album_id"] = album_id

    return client.post(
        MEDIA_URL,
        data=data,
        files={
            "file": (
                file_name,
                content,
                content_type,
            )
        },
        headers=headers,
    )


def test_upload_media_derives_scope_and_stores_original(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
) -> None:
    """Recebe mídia derivando o escopo institucional."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["organization_id"] == organization_id
    assert body["tenant_id"] == tenant_id
    assert body["environment_id"] == environment_id
    assert body["album_id"] == album_id
    assert body["original_name"] == "foto.jpg"
    assert body["media_type"] == "image"
    assert body["content_type"] == "image/jpeg"
    assert body["file_extension"] == ".jpg"
    assert body["file_size"] == len(b"conteudo-da-foto")
    assert len(body["checksum_sha256"]) == 64
    assert body["processing_status"] == "received"
    assert body["view_count"] == 0
    assert body["deleted_at"] is None

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / body["id"]
        / "original.jpg"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == b"conteudo-da-foto"


def test_upload_media_without_album(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Permite mídia ainda não vinculada a álbum."""

    _, _, environment_id, _, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["album_id"] is None


def test_list_media_filters_by_album(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista apenas as mídias vinculadas ao álbum informado."""

    _, _, environment_id, album_id, headers = media_context

    linked = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="vinculada.jpg",
    ).json()

    upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
        file_name="sem-album.jpg",
    )

    response = client.get(
        MEDIA_URL,
        params={
            "album_id": album_id,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert [
        media["id"]
        for media in response.json()
    ] == [
        linked["id"],
    ]


def test_get_media_by_id(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Consulta mídia pelo identificador."""

    _, _, environment_id, album_id, headers = media_context

    created = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    ).json()

    response = client.get(
        f"{MEDIA_URL}/{created['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == created


def test_download_original_media(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Baixa exatamente o arquivo original armazenado."""

    _, _, environment_id, album_id, headers = media_context

    content = b"imagem-original"

    created = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    ).json()

    response = client.get(
        f"{MEDIA_URL}/{created['id']}/original",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.content == content
    assert response.headers["content-type"] == "image/jpeg"


def test_delete_media_is_logical(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
) -> None:
    """Exclusão remove a mídia da consulta sem apagar o original."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    created = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    ).json()

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / created["id"]
        / "original.jpg"
    )

    response = client.delete(
        f"{MEDIA_URL}/{created['id']}",
        headers=headers,
    )

    assert response.status_code == 204
    assert response.content == b""
    assert original_path.is_file()

    get_response = client.get(
        f"{MEDIA_URL}/{created['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert (
        get_response.json()["error"]
        == "fotos_media_not_found"
    )


@pytest.mark.parametrize(
    ("content_type", "expected_status"),
    [
        ("application/pdf", 415),
        ("text/plain", 415),
    ],
)
def test_upload_media_rejects_invalid_type(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    content_type: str,
    expected_status: int,
) -> None:
    """Rejeita tipos não permitidos."""

    _, _, environment_id, album_id, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content_type=content_type,
    )

    assert response.status_code == expected_status


def test_upload_media_rejects_empty_file(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita arquivo sem conteúdo."""

    _, _, environment_id, album_id, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=b"",
    )

    assert response.status_code == 422


def test_unknown_media_returns_not_found(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Retorna 404 para mídia inexistente."""

    _, _, _, _, headers = media_context

    response = client.get(
        f"{MEDIA_URL}/{uuid4()}",
        headers=headers,
    )

    assert response.status_code == 404
    assert (
        response.json()["error"]
        == "fotos_media_not_found"
    )


def test_media_id_requires_36_characters(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita identificador inválido."""

    _, _, _, _, headers = media_context

    response = client.get(
        f"{MEDIA_URL}/invalid-id",
        headers=headers,
    )

    assert response.status_code == 422