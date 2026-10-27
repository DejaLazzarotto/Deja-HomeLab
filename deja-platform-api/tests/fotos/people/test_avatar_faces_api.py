from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from tests.fotos.curation.test_curation_api import ready_image
from tests.fotos.people.test_people_api import create_person


PEOPLE_URL = "/api/fotos/people"
CURATION_URL = "/api/fotos/curation"


def test_confirmed_face_can_be_used_as_avatar(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context

    person = create_person(
        client,
        environment_id,
        headers,
        name="Pessoa Avatar",
    )

    media_id = ready_image(
        client,
        environment_id,
        headers,
    )

    created = client.post(
        f"{CURATION_URL}/media/{media_id}/faces",
        json={
            "x": 0.20,
            "y": 0.20,
            "width": 0.40,
            "height": 0.40,
            "person_id": person["id"],
        },
        headers=headers,
    )

    assert created.status_code == 201, created.text
    face = created.json()
    assert face["status"] == "confirmed"

    base_url = f"{PEOPLE_URL}/{person['id']}/avatar/faces"

    listed = client.get(base_url, headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == face["id"]

    preview = client.get(
        f"{base_url}/{face['id']}/preview",
        headers=headers,
    )

    assert preview.status_code == 200, preview.text
    assert preview.headers["content-type"] == "image/webp"

    with Image.open(BytesIO(preview.content)) as image:
        assert image.format == "WEBP"
        assert image.size == (512, 512)

    saved = client.put(
        f"{base_url}/{face['id']}",
        headers=headers,
    )

    assert saved.status_code == 200, saved.text
    assert saved.json()["avatar_content_type"] == "image/webp"

    avatar = client.get(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=headers,
    )

    assert avatar.status_code == 200
    assert avatar.content == preview.content

    removed = client.delete(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=headers,
    )
    assert removed.status_code == 200, removed.text
    assert removed.json()["avatar_content_type"] is None

    missing = client.get(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=headers,
    )
    assert missing.status_code == 404

    person_response = client.get(
        f"{PEOPLE_URL}/{person['id']}",
        headers=headers,
    )
    assert person_response.status_code == 200

    faces_after_removal = client.get(base_url, headers=headers)
    assert faces_after_removal.status_code == 200
    assert faces_after_removal.json()["total"] == 1
    assert faces_after_removal.json()["items"][0]["id"] == face["id"]


def test_cannot_use_another_person_face_as_avatar(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context

    person_a = create_person(
        client, environment_id, headers, name="Pessoa A"
    )
    person_b = create_person(
        client, environment_id, headers, name="Pessoa B"
    )

    media_id = ready_image(client, environment_id, headers)

    created = client.post(
        f"{CURATION_URL}/media/{media_id}/faces",
        json={
            "x": 0.20,
            "y": 0.20,
            "width": 0.40,
            "height": 0.40,
            "person_id": person_a["id"],
        },
        headers=headers,
    )

    assert created.status_code == 201, created.text
    face_id = created.json()["id"]

    base_url = f"{PEOPLE_URL}/{person_b['id']}/avatar/faces"

    listed = client.get(base_url, headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 0

    preview = client.get(
        f"{base_url}/{face_id}/preview",
        headers=headers,
    )
    assert preview.status_code in (403, 404, 422)

    saved = client.put(
        f"{base_url}/{face_id}",
        headers=headers,
    )
    assert saved.status_code in (403, 404, 422)

    avatar = client.get(
        f"{PEOPLE_URL}/{person_b['id']}/avatar",
        headers=headers,
    )
    assert avatar.status_code == 404


def test_unconfirmed_face_cannot_be_used_as_avatar(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment_id, _, headers = media_context

    person = create_person(
        client, environment_id, headers, name="Pessoa Sem Confirmacao"
    )

    media_id = ready_image(client, environment_id, headers)

    created = client.post(
        f"{CURATION_URL}/media/{media_id}/faces",
        json={
            "x": 0.20,
            "y": 0.20,
            "width": 0.40,
            "height": 0.40,
        },
        headers=headers,
    )

    assert created.status_code == 201, created.text
    face = created.json()
    assert face["status"] != "confirmed"

    base_url = f"{PEOPLE_URL}/{person['id']}/avatar/faces"

    listed = client.get(base_url, headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 0

    preview = client.get(
        f"{base_url}/{face['id']}/preview",
        headers=headers,
    )
    assert preview.status_code in (403, 404, 422)

    saved = client.put(
        f"{base_url}/{face['id']}",
        headers=headers,
    )
    assert saved.status_code in (403, 404, 422)

    avatar = client.get(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=headers,
    )
    assert avatar.status_code == 404


def test_viewer_can_preview_but_cannot_change_avatar(
    client: TestClient,
    media_context: tuple,
    test_settings,
) -> None:
    from uuid import uuid4

    from tests.authentication.test_authentication_api import create_user
    from tests.authentication.test_user_authorization_api import authorization_headers

    organization_id, tenant_id, environment_id, _, admin = media_context

    person = create_person(
        client, environment_id, admin, name="Pessoa Visualizada"
    )
    media_id = ready_image(client, environment_id, admin)

    created = client.post(
        f"{CURATION_URL}/media/{media_id}/faces",
        json={
            "x": 0.20,
            "y": 0.20,
            "width": 0.40,
            "height": 0.40,
            "person_id": person["id"],
        },
        headers=admin,
    )
    assert created.status_code == 201, created.text
    face_id = created.json()["id"]

    viewer = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email=f"viewer.avatar.{uuid4().hex[:12]}@deja.com",
        role="viewer",
        module_access={"fotos": "viewer"},
    )
    viewer_headers = authorization_headers(test_settings, viewer)

    base_url = f"{PEOPLE_URL}/{person['id']}/avatar/faces"

    listed = client.get(base_url, headers=viewer_headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 1

    preview = client.get(
        f"{base_url}/{face_id}/preview",
        headers=viewer_headers,
    )
    assert preview.status_code == 200, preview.text
    assert preview.headers["content-type"] == "image/webp"

    saved = client.put(
        f"{base_url}/{face_id}",
        headers=viewer_headers,
    )
    assert saved.status_code == 403, saved.text

    avatar = client.get(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=admin,
    )
    assert avatar.status_code == 404


def test_avatar_faces_respect_environment_scope(
    client: TestClient,
    media_context: tuple,
    test_settings,
) -> None:
    from uuid import uuid4

    from tests.authentication.test_authentication_api import (
        create_environment,
        create_user,
    )
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )

    organization_id, tenant_id, environment_id, _, admin = media_context

    person = create_person(
        client,
        environment_id,
        admin,
        name="Pessoa do Ambiente A",
    )

    media_id = ready_image(client, environment_id, admin)

    created = client.post(
        f"{CURATION_URL}/media/{media_id}/faces",
        json={
            "x": 0.20,
            "y": 0.20,
            "width": 0.40,
            "height": 0.40,
            "person_id": person["id"],
        },
        headers=admin,
    )
    assert created.status_code == 201, created.text
    face_id = created.json()["id"]

    other_environment = create_environment(
        client,
        tenant_id,
        name="Ambiente B",
    )

    viewer = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=str(other_environment["id"]),
        email=f"viewer.scope.{uuid4().hex[:12]}@deja.com",
        role="viewer",
        module_access={"fotos": "viewer"},
    )

    viewer_headers = authorization_headers(test_settings, viewer)
    base_url = f"{PEOPLE_URL}/{person['id']}/avatar/faces"

    listed = client.get(base_url, headers=viewer_headers)
    assert listed.status_code == 403, listed.text

    preview = client.get(
        f"{base_url}/{face_id}/preview",
        headers=viewer_headers,
    )
    assert preview.status_code == 403, preview.text

    saved = client.put(
        f"{base_url}/{face_id}",
        headers=viewer_headers,
    )
    assert saved.status_code == 403, saved.text

    avatar = client.get(
        f"{PEOPLE_URL}/{person['id']}/avatar",
        headers=admin,
    )
    assert avatar.status_code == 404
