from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deja_platform_api.fotos.music.router import get_music_library
from deja_platform_api.fotos.music.library import VivaroMusicLibrary

MUSIC_URL = "/api/fotos/music"


@pytest.fixture()
def music_library(tmp_path: Path, test_app: FastAPI):
    music_dir = tmp_path / "vivaro-music"
    music_dir.mkdir()

    (music_dir / "primeira.mp3").write_bytes(b"primeira")
    (music_dir / "segunda.mp3").write_bytes(b"segunda")
    (music_dir / "arquivo.txt").write_text("ignorar")

    test_app.dependency_overrides[get_music_library] = (
        lambda: VivaroMusicLibrary(music_dir)
    )

    yield music_dir

    test_app.dependency_overrides.pop(get_music_library, None)


def test_music_list_requires_authentication(
    client: TestClient,
    music_library: Path,
) -> None:
    response = client.get(MUSIC_URL)

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_access_token"


def test_music_file_requires_authentication(
    client: TestClient,
    music_library: Path,
) -> None:
    response = client.get(f"{MUSIC_URL}/primeira.mp3")

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_access_token"

def test_platform_admin_lists_music(
    client: TestClient,
    test_settings,
    music_library: Path,
) -> None:
    from tests.authentication.test_authentication_api import create_user
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )

    administrator = create_user(
        client,
        None,
        email="platform.admin.vivaro.music@deja.com",
        role="platform_admin",
    )

    response = client.get(
        MUSIC_URL,
        headers=authorization_headers(test_settings, administrator),
    )

    assert response.status_code == 200
    assert response.json() == {
        "tracks": ["primeira.mp3", "segunda.mp3"],
    }


def test_platform_admin_downloads_music(
    client: TestClient,
    test_settings,
    music_library: Path,
) -> None:
    from tests.authentication.test_authentication_api import create_user
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )

    administrator = create_user(
        client,
        None,
        email="platform.admin.vivaro.download@deja.com",
        role="platform_admin",
    )

    response = client.get(
        f"{MUSIC_URL}/primeira.mp3",
        headers=authorization_headers(test_settings, administrator),
    )

    assert response.status_code == 200
    assert response.content == b"primeira"
    assert response.headers["content-type"] == "audio/mpeg"



@pytest.mark.parametrize(
    "endpoint",
    [
        MUSIC_URL,
        f"{MUSIC_URL}/primeira.mp3",
    ],
)
def test_user_without_fotos_module_cannot_access_music(
    client: TestClient,
    test_settings,
    music_library: Path,
    endpoint: str,
) -> None:
    from tests.authentication.test_authentication_api import (
        create_environment,
        create_organization,
        create_tenant,
        create_user,
    )
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="usuario.sem.fotos@deja.com",
        role="viewer",
    )

    response = client.get(
        endpoint,
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 403


@pytest.mark.parametrize("module_role", ["manager", "viewer"])
@pytest.mark.parametrize(
    "endpoint",
    [MUSIC_URL, f"{MUSIC_URL}/primeira.mp3"],
)
def test_authorized_fotos_user_accesses_music(
    client: TestClient,
    test_settings,
    music_library: Path,
    module_role: str,
    endpoint: str,
) -> None:
    from tests.authentication.test_authentication_api import (
        create_environment,
        create_organization,
        create_tenant,
        create_user,
    )
    from tests.authentication.test_user_authorization_api import (
        authorization_headers,
    )

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"{module_role}.vivaro.music@deja.com",
        role="viewer",
        module_access={"fotos": module_role},
    )

    response = client.get(
        endpoint,
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 200

    if endpoint == MUSIC_URL:
        assert response.json() == {
            "tracks": ["primeira.mp3", "segunda.mp3"],
        }
    else:
        assert response.content == b"primeira"
        assert response.headers["content-type"] == "audio/mpeg"
