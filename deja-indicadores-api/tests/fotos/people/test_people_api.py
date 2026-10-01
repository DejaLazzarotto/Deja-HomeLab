"""Testes de contrato da API de Pessoas do Deja Fotos."""

from collections.abc import Mapping
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)
from tests.fotos.media.test_media_api import (
    create_test_jpeg,
    upload_image,
)

PEOPLE_URL = "/api/fotos/people"


def create_person(
    client: TestClient,
    environment_id: str,
    headers: Mapping[str, str],
    *,
    name: str = "Ana",
    active: bool = True,
) -> dict[str, object]:
    response = client.post(
        PEOPLE_URL,
        json={
            "environment_id": environment_id,
            "name": name,
            "description": "Observação da família",
            "active": active,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_update_and_delete_person(
    client: TestClient,
    media_context: tuple,
) -> None:
    organization_id, tenant_id, environment_id, _, headers = (
        media_context
    )

    person = create_person(
        client,
        environment_id,
        headers,
        name=" Ana ",
    )
    assert person["name"] == "Ana"
    assert person["organization_id"] == organization_id
    assert person["tenant_id"] == tenant_id
    assert person["environment_id"] == environment_id
    assert person["avatar_content_type"] is None

    duplicate = client.post(
        PEOPLE_URL,
        json={
            "environment_id": environment_id,
            "name": "Ana",
        },
        headers=headers,
    )
    assert duplicate.status_code == 409

    updated = client.put(
        f"{PEOPLE_URL}/{person['id']}",
        json={
            "environment_id": environment_id,
            "name": "Ana Maria",
            "description": " Atualizada ",
            "active": False,
        },
        headers=headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == "Ana Maria"
    assert updated.json()["description"] == "Atualizada"

    listed = client.get(
        PEOPLE_URL,
        params={
            "environment_id": environment_id,
            "active": "false",
        },
        headers=headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == person["id"]

    deleted = client.delete(
        f"{PEOPLE_URL}/{person['id']}",
        headers=headers,
    )
    assert deleted.status_code == 204

    missing = client.get(
        f"{PEOPLE_URL}/{person['id']}",
        headers=headers,
    )
    assert missing.status_code == 404


def test_person_list_is_paginated(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context
    for name in ("Ana", "Bruna", "Clara"):
        create_person(
            client,
            environment_id,
            headers,
            name=name,
        )

    response = client.get(
        PEOPLE_URL,
        params={
            "environment_id": environment_id,
            "page": 2,
            "page_size": 1,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["total_pages"] == 3
    assert body["items"][0]["name"] == "Bruna"


def test_roles_and_institutional_scope(
    client: TestClient,
    test_settings: Settings,
    media_context: tuple,
) -> None:
    organization_id, tenant_id, environment_id, _, admin = (
        media_context
    )
    other_environment = create_environment(client, tenant_id, name="Homologação")
    other_environment_id = str(other_environment["id"])
    other_person = create_person(
        client,
        other_environment_id,
        admin,
    )

    viewer = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="viewer.people@deja.com",
        role="viewer",
        module_access={"fotos": "viewer"},
    )
    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )
    assert client.get(
        PEOPLE_URL,
        headers=viewer_headers,
    ).status_code == 200
    assert client.post(
        PEOPLE_URL,
        json={
            "environment_id": environment_id,
            "name": "Sem permissão",
        },
        headers=viewer_headers,
    ).status_code == 403
    assert client.get(
        f"{PEOPLE_URL}/{other_person['id']}",
        headers=viewer_headers,
    ).status_code == 403
    assert client.get(
        PEOPLE_URL,
        params={"environment_id": other_environment_id},
        headers=viewer_headers,
    ).status_code == 403

    analyst = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="analyst.people@deja.com",
        role="analyst",
        module_access={"fotos": "analyst"},
    )
    analyst_headers = authorization_headers(
        test_settings,
        analyst,
    )
    person = create_person(
        client,
        environment_id,
        analyst_headers,
        name="Bruna",
    )
    assert client.delete(
        f"{PEOPLE_URL}/{person['id']}",
        headers=analyst_headers,
    ).status_code == 403


def test_person_media_link_and_scope(
    client: TestClient,
    test_settings: Settings,
    media_context: tuple,
) -> None:
    organization_id, tenant_id, environment_id, _, headers = (
        media_context
    )
    person = create_person(client, environment_id, headers)
    media_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
    )
    assert media_response.status_code == 201, media_response.text
    media_id = media_response.json()["id"]

    linked = client.post(
        f"{PEOPLE_URL}/{person['id']}/media",
        json={"media_id": media_id},
        headers=headers,
    )
    assert linked.status_code == 204, linked.text

    gallery = client.get(
        f"{PEOPLE_URL}/{person['id']}/media",
        params={"page": 1, "page_size": 1},
        headers=headers,
    )
    assert gallery.status_code == 200
    assert gallery.json()["total"] == 1
    assert gallery.json()["items"][0]["id"] == media_id

    analyst = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="analyst.links@deja.com",
        role="analyst",
        module_access={"fotos": "analyst"},
    )
    analyst_headers = authorization_headers(
        test_settings,
        analyst,
    )
    assert client.post(
        f"{PEOPLE_URL}/{person['id']}/media",
        json={"media_id": media_id},
        headers=analyst_headers,
    ).status_code == 403

    other_environment = create_environment(client, tenant_id, name="Homologação")
    other_media = upload_image(
        client,
        environment_id=str(other_environment["id"]),
        album_id=None,
        headers=headers,
        content=create_test_jpeg(width=19),
    )
    assert other_media.status_code == 201, other_media.text
    assert client.post(
        f"{PEOPLE_URL}/{person['id']}/media",
        json={"media_id": other_media.json()["id"]},
        headers=headers,
    ).status_code == 409

    removed = client.delete(
        f"{PEOPLE_URL}/{person['id']}/media/{media_id}",
        headers=headers,
    )
    assert removed.status_code == 204
    assert client.get(
        f"{PEOPLE_URL}/{person['id']}/media",
        headers=headers,
    ).json()["total"] == 0


def test_avatar_upload_read_remove_and_delete(
    client: TestClient,
    test_settings: Settings,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context
    person = create_person(client, environment_id, headers)
    url = f"{PEOPLE_URL}/{person['id']}/avatar"

    uploaded = client.put(
        url,
        files={
            "file": (
                "perfil.jpg",
                create_test_jpeg(width=640, height=480),
                "image/jpeg",
            )
        },
        headers=headers,
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["avatar_content_type"] == "image/webp"

    avatar = client.get(url, headers=headers)
    assert avatar.status_code == 200
    with Image.open(BytesIO(avatar.content)) as image:
        assert image.format == "WEBP"
        assert image.width <= 512
        assert image.height <= 512

    avatar_files = list(
        test_settings.uploads_dir.rglob(
            f"{person['id']}/avatars/*.webp"
        )
    )
    assert len(avatar_files) == 1

    invalid = client.put(
        url,
        files={
            "file": (
                "perfil.jpg",
                b"arquivo invalido",
                "image/jpeg",
            )
        },
        headers=headers,
    )
    assert invalid.status_code == 422
    assert client.get(url, headers=headers).status_code == 200

    removed = client.delete(url, headers=headers)
    assert removed.status_code == 200
    assert removed.json()["avatar_content_type"] is None
    assert client.get(url, headers=headers).status_code == 404
    assert not avatar_files[0].exists()

    again = client.put(
        url,
        files={
            "file": (
                "novo.jpg",
                create_test_jpeg(width=24),
                "image/jpeg",
            )
        },
        headers=headers,
    )
    assert again.status_code == 200
    assert client.delete(
        f"{PEOPLE_URL}/{person['id']}",
        headers=headers,
    ).status_code == 204
    assert not list(
        test_settings.uploads_dir.rglob(
            f"{person['id']}/avatars/*.webp"
        )
    )