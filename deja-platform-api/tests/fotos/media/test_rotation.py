"""Testes da geometria de rotação das fotografias."""

import pytest
from tests.fotos.media.test_media_api import media_context  # noqa: F401

from deja_platform_api.fotos.media.rotation_geometry import (
    rotate_face_box,
    rotation_delta,
)


@pytest.mark.parametrize(
    ("current", "target", "expected"),
    [
        (0, 90, 90),
        (90, 180, 90),
        (180, 90, 270),
        (270, 0, 90),
        (90, 90, 0),
    ],
)
def test_rotation_delta(current, target, expected):
    assert rotation_delta(current, target) == expected


@pytest.mark.parametrize("degrees", [90, 180, 270])
def test_rotate_face_box_preserves_coordinates_after_inverse(degrees):
    original = (0.1, 0.2, 0.3, 0.4)
    rotated = rotate_face_box(*original, degrees)
    restored = rotate_face_box(*rotated, (360 - degrees) % 360)

    assert restored == pytest.approx(original)


def test_invalid_rotation_is_rejected():
    with pytest.raises(ValueError):
        rotation_delta(0, 45)


def test_rotation_persists_and_regenerates_derivatives(
    client,
    media_context,
    test_settings,
):
    """Valida a rotação persistente e preservação do original."""

    from PIL import Image
    from tests.fotos.media.test_media_api import (
        MEDIA_URL,
        create_test_jpeg,
        upload_image,
    )

    _, _, environment_id, album_id, headers = media_context

    original = create_test_jpeg(width=120, height=80)

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=original,
    )
    assert response.status_code == 201, response.text

    media_id = response.json()["id"]

    processed = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )
    assert processed.status_code == 200, processed.text

    before = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )
    assert before.status_code == 200, before.text
    assert before.json()["id"] == media_id

    rotated = client.patch(
        f"{MEDIA_URL}/{media_id}/rotation",
        json={"rotation_degrees": 90},
        headers=headers,
    )
    assert rotated.status_code == 200, rotated.text
    assert rotated.json()["rotation_degrees"] == 90

    after = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )
    assert after.status_code == 200
    assert after.json()["rotation_degrees"] == 90
    original_response = client.get(
        f"{MEDIA_URL}/{media_id}/original",
        headers=headers,
    )
    assert original_response.status_code == 200, original_response.text
    assert original_response.content == original

    preview = client.get(
        f"{MEDIA_URL}/{media_id}/preview",
        headers=headers,
    )
    assert preview.status_code == 200, preview.text

    from io import BytesIO

    with Image.open(BytesIO(preview.content)) as image:
        assert image.size == (80, 120)


def test_rotation_updates_face_coordinates(
    client,
    media_context,
    test_session_factory,
):
    """Confirma a atualização persistente das coordenadas faciais."""

    from uuid import uuid4

    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from tests.fotos.media.test_media_api import (
        MEDIA_URL,
        create_test_jpeg,
        upload_image,
    )

    organization_id, tenant_id, environment_id, album_id, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(width=200, height=100),
    )
    assert response.status_code == 201, response.text

    media_id = response.json()["id"]

    processed = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )
    assert processed.status_code == 200, processed.text

    face_id = str(uuid4())

    with test_session_factory() as session:
        session.add(
            FotosFaceModel(
                id=face_id,
                media_id=media_id,
                organization_id=organization_id,
                tenant_id=tenant_id,
                environment_id=environment_id,
                x=0.1,
                y=0.2,
                width=0.3,
                height=0.4,
                origin="manual",
                status="unknown",
            )
        )
        session.commit()

    rotated = client.patch(
        f"{MEDIA_URL}/{media_id}/rotation",
        json={"rotation_degrees": 90},
        headers=headers,
    )
    assert rotated.status_code == 200, rotated.text

    with test_session_factory() as session:
        face = session.get(FotosFaceModel, face_id)
        assert face is not None
        assert (
            face.x,
            face.y,
            face.width,
            face.height,
        ) == pytest.approx((0.4, 0.1, 0.4, 0.3))

def test_rotation_rolls_back_on_commit_failure(
    client,
    media_context,
    test_session_factory,
    test_settings,
    monkeypatch,
):
    """Preserva banco e arquivos anteriores se o commit falhar."""

    from pathlib import Path

    from deja_platform_api.fotos.media.models import FotosMediaModel
    from deja_platform_api.fotos.media.repository import FotosMediaRepository
    from tests.fotos.media.test_media_api import (
        MEDIA_URL,
        create_test_jpeg,
        upload_image,
    )

    _, _, environment_id, album_id, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(width=120, height=80),
    )
    assert response.status_code == 201, response.text

    media_id = response.json()["id"]

    processed = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )
    assert processed.status_code == 200, processed.text

    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        assert media.rotation_degrees == 0

    derivatives_before = set(test_settings.uploads_dir.rglob("*.webp"))

    def simulated_failure(self, media):
        raise RuntimeError("Falha simulada no commit.")

    monkeypatch.setattr(
        FotosMediaRepository,
        "update",
        simulated_failure,
    )

    with pytest.raises(RuntimeError, match="Falha simulada"):
        client.patch(
            f"{MEDIA_URL}/{media_id}/rotation",
            json={"rotation_degrees": 90},
            headers=headers,
        )

    assert set(test_settings.uploads_dir.rglob("*.webp")) == derivatives_before

    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        assert media.rotation_degrees == 0

    preview = client.get(
        f"{MEDIA_URL}/{media_id}/preview",
        headers=headers,
    )
    assert preview.status_code == 200

    from io import BytesIO
    from PIL import Image

    with Image.open(BytesIO(preview.content)) as image:
        assert image.size == (120, 80)

def test_rotation_successive_changes(
    client,
    media_context,
    test_session_factory,
):
    """Valida rotacoes sucessivas e retorno a orientacao original."""

    from uuid import uuid4

    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from tests.fotos.media.test_media_api import (
        MEDIA_URL,
        create_test_jpeg,
        upload_image,
    )

    org, tenant, environment, album, headers = media_context

    response = upload_image(
        client,
        environment_id=environment,
        album_id=album,
        headers=headers,
        content=create_test_jpeg(width=200, height=100),
    )
    assert response.status_code == 201, response.text
    media_id = response.json()["id"]

    processed = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )
    assert processed.status_code == 200, processed.text

    face_id = str(uuid4())
    original = (0.1, 0.2, 0.3, 0.4)

    with test_session_factory() as session:
        session.add(
            FotosFaceModel(
                id=face_id,
                media_id=media_id,
                organization_id=org,
                tenant_id=tenant,
                environment_id=environment,
                x=original[0],
                y=original[1],
                width=original[2],
                height=original[3],
                origin="manual",
                status="unknown",
            )
        )
        session.commit()

    for angle, expected in (
        (90, (0.4, 0.1, 0.4, 0.3)),
        (180, (0.6, 0.4, 0.3, 0.4)),
        (0, original),
    ):
        response = client.patch(
            f"{MEDIA_URL}/{media_id}/rotation",
            json={"rotation_degrees": angle},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["rotation_degrees"] == angle

        with test_session_factory() as session:
            face = session.get(FotosFaceModel, face_id)
            assert face is not None
            assert (
                face.x,
                face.y,
                face.width,
                face.height,
            ) == pytest.approx(expected)