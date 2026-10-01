"""Contratos de marcação, revisão, escopo e referências faciais."""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.curation import engine
from deja_indicadores_api.fotos.curation.models import FotosFaceModel
from deja_indicadores_api.fotos.curation.service import same_face_box
from tests.authentication.test_authentication_api import create_environment, create_user
from tests.authentication.test_user_authorization_api import authorization_headers
from tests.fotos.media.test_media_api import upload_image, upload_video
from tests.fotos.people.test_people_api import create_person

CURATION = "/api/fotos/curation"


def test_detected_box_overlapping_a_larger_manual_box_is_the_same_face() -> None:
    manual = FotosFaceModel(x=0.20, y=0.25, width=0.50, height=0.65)
    assert same_face_box(manual, (0.26, 0.30, 0.41, 0.55))
    assert not same_face_box(manual, (0.72, 0.30, 0.20, 0.20))


def image_bytes() -> bytes:
    image = Image.new("RGB", (120, 120))
    image.putdata([(x * 2, y * 2, (x + y) % 256) for y in range(120) for x in range(120)])
    output = BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()


def ready_image(
    client: TestClient, env: str, headers: dict, *, content: bytes | None = None
) -> str:
    upload = upload_image(
        client, environment_id=env, album_id=None, headers=headers,
        content=content if content is not None else image_bytes(),
    )
    assert upload.status_code == 201, upload.text
    media_id = upload.json()["id"]
    processed = client.post(f"/api/fotos/media/{media_id}/process", headers=headers)
    assert processed.status_code == 200, processed.text
    return media_id


def ready_video(client: TestClient, env: str, headers: dict) -> str:
    upload = upload_video(
        client, environment_id=env, album_id=None, headers=headers,
    )
    assert upload.status_code == 201, upload.text
    media_id = upload.json()["id"]
    processed = client.post(f"/api/fotos/media/{media_id}/process", headers=headers)
    assert processed.status_code == 200, processed.text
    return media_id


def test_video_rejects_facial_detection(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment, _, headers = media_context
    media_id = ready_video(client, environment, headers)

    response = client.post(
        f"{CURATION}/media/{media_id}/detect",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "fotos_face_invalid"


def test_video_rejects_manual_face_marking(
    client: TestClient,
    media_context: tuple,
) -> None:
    _, _, environment, _, headers = media_context
    media_id = ready_video(client, environment, headers)

    response = client.post(
        f"{CURATION}/media/{media_id}/faces",
        json={"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.5},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "fotos_face_invalid"


def test_video_rejects_teaching_legacy_face(
    client: TestClient,
    media_context: tuple,
    test_session_factory,
) -> None:
    organization, tenant, environment, _, headers = media_context
    person = create_person(client, environment, headers, name="Pessoa do vídeo")
    media_id = ready_video(client, environment, headers)

    face = FotosFaceModel(
        id=str(uuid4()),
        media_id=media_id,
        organization_id=organization,
        tenant_id=tenant,
        environment_id=environment,
        x=0.1,
        y=0.1,
        width=0.5,
        height=0.5,
        origin="manual",
        status="confirmed",
        person_id=person["id"],
    )

    with test_session_factory() as session:
        session.add(face)
        session.commit()

    response = client.post(f"{CURATION}/faces/{face.id}/teach", headers=headers)

    assert response.status_code == 409
    assert response.json()["error"] == "fotos_face_invalid"


def test_real_engine_rejects_a_nonface_reference(tmp_path: Path) -> None:
    blank = tmp_path / "blank.png"
    Image.new("RGB", (128, 128), "white").save(blank)
    assert engine.detect(blank, Path("models/fotos")) == []
    pattern = Image.new("RGB", (128, 128))
    pattern.putdata([(x * 2, y * 2, (x ^ y) * 2) for y in range(128) for x in range(128)])
    reference = tmp_path / "reference.webp"
    pattern.save(reference, format="WEBP", lossless=True)
    assert engine.suggest(pattern, [("known-person", reference)], Path("models/fotos")) is None


def test_manual_marking_review_teaching_and_pagination(
    client: TestClient,
    media_context: tuple,
    monkeypatch,
) -> None:
    _, _, environment, _, headers = media_context
    person = create_person(client, environment, headers, name="Katia")
    media_id = ready_image(client, environment, headers)
    payload = {"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.5, "person_id": person["id"]}
    created = client.post(f"{CURATION}/media/{media_id}/faces", json=payload, headers=headers)
    assert created.status_code == 201, created.text
    face = created.json()
    assert face["status"] == "confirmed"
    assert face["origin"] == "manual"
    assert (
        client.get(f"/api/fotos/people/{person['id']}/media", headers=headers).json()["total"] == 1
    )
    assert (
        client.get(f"{CURATION}/media", params={"person_id": person["id"]}, headers=headers)
        .json()["total"]
        == 1
    )
    invalid = client.post(
        f"{CURATION}/media/{media_id}/faces",
        json={"x": 0.9, "y": 0.9, "width": 0.5, "height": 0.5},
        headers=headers,
    )
    assert invalid.status_code == 422

    monkeypatch.setattr(engine, "validate_reference", lambda crop, models_dir: True)
    taught = client.post(f"{CURATION}/faces/{face['id']}/teach", headers=headers)
    assert taught.status_code == 200, taught.text
    assert (
        client.post(f"{CURATION}/faces/{face['id']}/teach", headers=headers).json()["id"]
        == taught.json()["id"]
    )
    references = client.get(
        f"{CURATION}/people/{person['id']}/references",
        params={"page": 1, "page_size": 1},
        headers=headers,
    )
    assert references.json()["total"] == 1
    assert (
        client.get(
            f"{CURATION}/references/{taught.json()['id']}/image", headers=headers
        ).status_code
        == 200
    )
    listed = client.get(
        f"{CURATION}/media/{media_id}/faces",
        params={"page": 1, "page_size": 1},
        headers=headers,
    )
    assert listed.json()["total"] == 1
    assert (
        client.delete(
            f"/api/fotos/people/{person['id']}/media/{media_id}", headers=headers
        ).status_code
        == 409
    )
    assert client.delete(f"{CURATION}/faces/{face['id']}", headers=headers).status_code == 204
    assert (
        client.get(f"{CURATION}/people/{person['id']}/references", headers=headers).json()["total"]
        == 0
    )
    # A remoção da caixa não apaga vínculos já confirmados ou anteriores.
    assert (
        client.get(f"/api/fotos/people/{person['id']}/media", headers=headers).json()["total"] == 1
    )


def test_detect_suggest_reject_and_scope(
    client: TestClient,
    test_settings: Settings,
    media_context: tuple,
    monkeypatch,
) -> None:
    org, tenant, environment, _, admin = media_context
    person = create_person(client, environment, admin, name="Maria")
    media_id = ready_image(client, environment, admin)
    seed = client.post(
        f"{CURATION}/media/{media_id}/faces",
        json={"x": 0.05, "y": 0.05, "width": 0.4, "height": 0.4, "person_id": person["id"]},
        headers=admin,
    )
    assert seed.status_code == 201, seed.text
    monkeypatch.setattr(engine, "validate_reference", lambda crop, models_dir: True)
    taught = client.post(f"{CURATION}/faces/{seed.json()['id']}/teach", headers=admin)
    assert taught.status_code == 200
    reference_id = taught.json()["id"]
    monkeypatch.setattr(engine, "detect", lambda path, models_dir: [(0.55, 0.55, 0.4, 0.4)])
    monkeypatch.setattr(engine, "suggest", lambda crop, refs, models_dir: (person["id"], 0.82))
    detected = client.post(f"{CURATION}/media/{media_id}/detect", headers=admin)
    assert detected.status_code == 200, detected.text
    face = detected.json()[0]
    assert face["status"] == "suggested"
    assert client.post(f"{CURATION}/media/{media_id}/detect", headers=admin).json() == []
    assert (
        client.get(
            f"{CURATION}/summary", params={"environment_id": environment}, headers=admin
        ).json()["pending"]
        == 1
    )
    rejected = client.post(f"{CURATION}/faces/{face['id']}/reject", headers=admin)
    assert rejected.json()["status"] == "rejected"
    assert rejected.json()["person_id"] is None
    assert (
        client.post(
            f"{CURATION}/faces/{face['id']}/confirm",
            json={"person_id": person["id"]},
            headers=admin,
        ).json()["status"]
        == "confirmed"
    )

    other = create_environment(client, tenant, name="Outro ambiente")
    other_person = create_person(client, str(other["id"]), admin, name="Outra")
    mismatch = client.post(
        f"{CURATION}/faces/{face['id']}/confirm",
        json={"person_id": other_person["id"]},
        headers=admin,
    )
    assert mismatch.status_code == 409
    viewer = create_user(
        client,
        org,
        tenant_id=tenant,
        environment_id=environment,
        email="viewer.faces@deja.com",
        role="viewer",
        module_access={"fotos": "viewer"},
    )
    headers = authorization_headers(test_settings, viewer)
    assert client.get(f"{CURATION}/media/{media_id}/faces", headers=headers).status_code == 200
    assert client.post(f"{CURATION}/media/{media_id}/detect", headers=headers).status_code == 403
    assert (
        client.get(
            f"{CURATION}/people/{other_person['id']}/references", headers=headers
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"{CURATION}/media", params={"environment_id": str(other["id"])}, headers=headers
        ).status_code
        == 403
    )
    assert client.delete(f"/api/fotos/people/{person['id']}", headers=admin).status_code == 204
    remaining = client.get(f"{CURATION}/media/{media_id}/faces", headers=admin).json()["items"]
    assert all(face["status"] == "unknown" and face["person_id"] is None for face in remaining)
    assert (
        client.get(f"{CURATION}/references/{reference_id}/image", headers=admin).status_code == 404
    )


def test_analysis_rechecks_existing_unknown_after_teaching(
    client: TestClient,
    media_context: tuple,
    monkeypatch,
) -> None:
    _, _, environment, _, headers = media_context
    person = create_person(client, environment, headers, name="Máximo")
    taught_media = ready_image(client, environment, headers)
    seed = client.post(
        f"{CURATION}/media/{taught_media}/faces",
        json={"x": 0.05, "y": 0.05, "width": 0.4, "height": 0.4,
              "person_id": person["id"]},
        headers=headers,
    )
    assert seed.status_code == 201
    monkeypatch.setattr(engine, "validate_reference", lambda crop, models_dir: True)
    assert client.post(
        f"{CURATION}/faces/{seed.json()['id']}/teach", headers=headers
    ).status_code == 200

    alternate = BytesIO()
    Image.new("RGB", (120, 120), "purple").save(alternate, format="JPEG")
    other_media = ready_image(client, environment, headers, content=alternate.getvalue())
    unknown = client.post(
        f"{CURATION}/media/{other_media}/faces",
        json={"x": 0.05, "y": 0.05, "width": 0.4, "height": 0.4},
        headers=headers,
    )
    assert unknown.status_code == 201
    face_id = unknown.json()["id"]
    monkeypatch.setattr(engine, "detect", lambda path, models_dir: [(0.05, 0.05, 0.4, 0.4)])
    monkeypatch.setattr(engine, "suggest", lambda crop, refs, models_dir: (person["id"], 0.82))

    analysed = client.post(f"{CURATION}/media/{other_media}/detect", headers=headers)
    assert analysed.status_code == 200, analysed.text
    assert len(analysed.json()) == 1
    assert analysed.json()[0]["id"] == face_id
    assert analysed.json()[0]["status"] == "suggested"
    assert analysed.json()[0]["person_id"] == person["id"]
    listed = client.get(f"{CURATION}/media/{other_media}/faces", headers=headers).json()
    assert listed["total"] == 1
    assert listed["items"][0]["status"] == "suggested"
    assert client.post(f"{CURATION}/media/{other_media}/detect", headers=headers).json() == []
    rejected = client.post(f"{CURATION}/faces/{face_id}/reject", headers=headers)
    assert rejected.status_code == 200
    assert client.post(f"{CURATION}/media/{other_media}/detect", headers=headers).json() == []
    final = client.get(f"{CURATION}/media/{other_media}/faces", headers=headers).json()
    assert final["total"] == 1
    assert final["items"][0]["status"] == "rejected"
