"""Contratos de marcação, revisão, escopo e referências faciais."""

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.curation import engine
from tests.authentication.test_authentication_api import create_environment, create_user
from tests.authentication.test_user_authorization_api import authorization_headers
from tests.fotos.media.test_media_api import upload_image
from tests.fotos.people.test_people_api import create_person

CURATION = "/api/fotos/curation"


def image_bytes() -> bytes:
    image = Image.new("RGB", (120, 120))
    image.putdata([(x * 2, y * 2, (x + y) % 256) for y in range(120) for x in range(120)])
    output = BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()


def ready_image(client: TestClient, env: str, headers: dict) -> str:
    upload = upload_image(
        client, environment_id=env, album_id=None, headers=headers, content=image_bytes()
    )
    assert upload.status_code == 201, upload.text
    media_id = upload.json()["id"]
    processed = client.post(f"/api/fotos/media/{media_id}/process", headers=headers)
    assert processed.status_code == 200, processed.text
    return media_id


def test_real_engine_detects_no_face_and_matches_reference(tmp_path: Path) -> None:
    blank = tmp_path / "blank.png"
    Image.new("RGB", (128, 128), "white").save(blank)
    assert engine.detect(blank) == []
    pattern = Image.new("RGB", (128, 128))
    pattern.putdata([(x * 2, y * 2, (x ^ y) * 2) for y in range(128) for x in range(128)])
    reference = tmp_path / "reference.webp"
    pattern.save(reference, format="WEBP", lossless=True)
    match = engine.suggest(pattern, [("known-person", reference)])
    assert match is not None
    assert match[0] == "known-person"


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

    monkeypatch.setattr(engine, "_cv2", lambda: object())
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
    monkeypatch.setattr(engine, "_cv2", lambda: object())
    taught = client.post(f"{CURATION}/faces/{seed.json()['id']}/teach", headers=admin)
    assert taught.status_code == 200
    reference_id = taught.json()["id"]
    monkeypatch.setattr(engine, "detect", lambda path: [(0.55, 0.55, 0.4, 0.4)])
    monkeypatch.setattr(engine, "suggest", lambda crop, refs: (person["id"], 0.82))
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
