"""Testes de contrato da API de Pessoas do Deja Fotos."""

from collections.abc import Mapping
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from deja_platform_api.core.config import Settings
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
    other_environment = create_environment(
        client,
        tenant_id,
        name="Homologação",
    )
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

    assert client.get(
        PEOPLE_URL,
        headers=analyst_headers,
    ).status_code == 403

    assert client.post(
        PEOPLE_URL,
        json={
            "environment_id": environment_id,
            "name": "Analista sem permissão",
        },
        headers=analyst_headers,
    ).status_code == 403

    manager = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="manager.people@deja.com",
        role="user",
        module_access={"fotos": "manager"},
    )
    manager_headers = authorization_headers(
        test_settings,
        manager,
    )

    person = create_person(
        client,
        environment_id,
        manager_headers,
        name="Bruna",
    )

    assert client.delete(
        f"{PEOPLE_URL}/{person['id']}",
        headers=manager_headers,
    ).status_code == 204

def test_person_media_link_and_scope(
    client: TestClient,
    test_settings: Settings,
    media_context: tuple,
) -> None:
    organization_id, tenant_id, environment_id, _, headers = (
        media_context
    )

    person = create_person(
        client,
        environment_id,
        headers,
    )

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
        params={
            "page": 1,
            "page_size": 1,
        },
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

    other_environment = create_environment(
        client,
        tenant_id,
        name="Homologação",
    )

    other_media = upload_image(
        client,
        environment_id=str(other_environment["id"]),
        album_id=None,
        headers=headers,
        content=create_test_jpeg(
            width=19,
        ),
    )

    assert other_media.status_code == 201, other_media.text

    assert client.post(
        f"{PEOPLE_URL}/{person['id']}/media",
        json={
            "media_id": other_media.json()["id"],
        },
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

def test_avatar_manual_upload_unavailable(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context
    person = create_person(client, environment_id, headers)
    url = f"{PEOPLE_URL}/{person['id']}/avatar"

    assert client.get(url, headers=headers).status_code == 404

    response = client.put(
        url,
        files={
            "file": (
                "perfil.jpg",
                create_test_jpeg(width=24),
                "image/jpeg",
            )
        },
        headers=headers,
    )
    assert response.status_code == 405

    assert client.delete(
        f"{PEOPLE_URL}/{person['id']}",
        headers=headers,
    ).status_code == 204


def test_person_media_periods_and_filters(
    client: TestClient,
    media_context: tuple,
) -> None:
    """Valida agrupamento e filtros sem misturar outras pessoas."""

    _, _, environment_id, _, headers = media_context
    person = create_person(client, environment_id, headers, name="Periodo")
    other_person = create_person(client, environment_id, headers, name="Outra")

    media_ids = []

    for width in (31, 32, 33, 34):
        uploaded = upload_image(
            client,
            environment_id=environment_id,
            album_id=None,
            headers=headers,
            content=create_test_jpeg(width=width),
        )
        assert uploaded.status_code == 201, uploaded.text
        media_ids.append(uploaded.json()["id"])

    for media_id, date in (
        (media_ids[0], "2020-04-26T12:00:00"),
        (media_ids[1], "2021-10-15T12:00:00"),
        (media_ids[3], "2020-04-27T12:00:00"),
    ):
        updated = client.patch(
            f"/api/fotos/media/{media_id}/original-date",
            json={
                "original_date": date,
                "original_date_precision": "date",
            },
            headers=headers,
        )
        assert updated.status_code == 200, updated.text

    for media_id in media_ids[:3]:
        linked = client.post(
            f"{PEOPLE_URL}/{person['id']}/media",
            json={"media_id": media_id},
            headers=headers,
        )
        assert linked.status_code == 204, linked.text

    other_link = client.post(
        f"{PEOPLE_URL}/{other_person['id']}/media",
        json={"media_id": media_ids[3]},
        headers=headers,
    )
    assert other_link.status_code == 204, other_link.text

    base = f"{PEOPLE_URL}/{person['id']}/media"

    periods = client.get(f"{base}/periods", headers=headers)
    assert periods.status_code == 200, periods.text
    assert periods.json() == [
        {"year": 2021, "month": 10, "media_count": 1},
        {"year": 2020, "month": 4, "media_count": 1},
        {"year": None, "month": None, "media_count": 1},
    ]

    april = client.get(
        base,
        params={"year": 2020, "month": 4, "page_size": 30},
        headers=headers,
    )
    assert april.status_code == 200, april.text
    assert april.json()["total"] == 1
    assert [item["id"] for item in april.json()["items"]] == [
        media_ids[0]
    ]

    undated = client.get(
        base,
        params={"without_date": "true", "page_size": 30},
        headers=headers,
    )
    assert undated.status_code == 200, undated.text
    assert undated.json()["total"] == 1
    assert undated.json()["items"][0]["id"] == media_ids[2]

    all_media = client.get(base, headers=headers)
    assert all_media.status_code == 200, all_media.text
    assert all_media.json()["total"] == 3