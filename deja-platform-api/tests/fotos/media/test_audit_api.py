"""Testes da auditoria do acervo e da precisão de datas em lote."""

from uuid import uuid4
from datetime import datetime

from deja_platform_api.fotos.curation.models import FotosFaceModel
from tests.fotos.media.test_media_api import (
    MEDIA_URL,
    create_test_jpeg,
    media_context,  # noqa: F401
    upload_image,
)


def mark_audit_ready(test_session_factory, *media_ids):
    """Conclui a curadoria para incluir fotografias no escopo da Auditoria."""
    from deja_platform_api.fotos.media.models import FotosMediaModel

    with test_session_factory() as session:
        for media_id in media_ids:
            media = session.get(FotosMediaModel, media_id)
            assert media is not None
            media.curation_completed = True
        session.commit()


def test_audit_filters_and_bulk_date_preserve_album(
    client,
    media_context,
    test_session_factory,
):
    organization_id, tenant_id, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="auditoria.jpg",
        content=create_test_jpeg(width=32, height=24),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    processed = client.post(f"{MEDIA_URL}/{media_id}/process", headers=headers)
    assert processed.status_code == 200, processed.text
    mark_audit_ready(test_session_factory, media_id)

    params = {"environment_id": environment_id}
    summary = client.get(f"{MEDIA_URL}/audit/summary", params=params, headers=headers)
    assert summary.status_code == 200, summary.text
    assert summary.json()["without_date"] == 1
    assert summary.json()["without_album"] == 0

    without_date = client.get(
        f"{MEDIA_URL}/audit/media",
        params={**params, "category": "without_date"},
        headers=headers,
    )
    assert without_date.status_code == 200, without_date.text
    assert without_date.json()["total"] == 1
    assert without_date.json()["items"][0]["album_id"] == album_id

    updated = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_original_date",
            "media_ids": [media_id],
            "original_date": "1986-07-12T12:00:00",
            "original_date_precision": "date",
        },
        headers=headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["succeeded_count"] == 1
    assert updated.json()["results"][0]["media"]["original_date_precision"] == "date"
    assert updated.json()["results"][0]["media"]["album_id"] == album_id

    summary = client.get(f"{MEDIA_URL}/audit/summary", params=params, headers=headers)
    assert summary.status_code == 200
    assert summary.json()["without_date"] == 0
    assert summary.json()["without_time"] == 1
    assert summary.json()["without_album"] == 0


def test_audit_includes_unconfirmed_suggestion_inside_album(
    client,
    media_context,
    test_session_factory,
):
    org_id, tenant_id, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(width=48, height=36),
    )
    assert uploaded.status_code == 201
    media_id = uploaded.json()["id"]
    assert client.post(f"{MEDIA_URL}/{media_id}/process", headers=headers).status_code == 200
    mark_audit_ready(test_session_factory, media_id)
    with test_session_factory() as session:
        session.add(FotosFaceModel(
            id=str(uuid4()),
            media_id=media_id,
            organization_id=org_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            x=0.1, y=0.1, width=0.5, height=0.5,
            origin="detected", status="suggested",
        ))
        session.commit()

    response = client.get(
        f"{MEDIA_URL}/audit/media",
        params={"environment_id": environment_id, "category": "pending_faces"},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["id"] == media_id
    assert response.json()["items"][0]["album_id"] == album_id


def test_audit_reopens_face_curation_preserving_albums_and_suggestions(
    client, media_context, test_session_factory,
):
    """Reabrir curadoria pela auditoria não desvincula fotos nem apaga rostos."""
    from deja_platform_api.fotos.media.models import FotosMediaModel

    organization_id, tenant_id, environment_id, album_id, headers = media_context
    ids = []
    for selected_album in (album_id, None):
        response = upload_image(
            client,
            environment_id=environment_id,
            album_id=selected_album,
            headers=headers,
            content=create_test_jpeg(width=32 + len(ids), height=27),
        )
        assert response.status_code == 201, response.text
        media_id = response.json()["id"]
        ids.append(media_id)
        assert client.post(
            f"{MEDIA_URL}/{media_id}/process", headers=headers
        ).status_code == 200

    with test_session_factory() as session:
        for media_id in ids:
            media = session.get(FotosMediaModel, media_id)
            assert media is not None
            media.curation_completed = True
            session.add(FotosFaceModel(
                id=str(uuid4()),
                media_id=media_id,
                organization_id=organization_id,
                tenant_id=tenant_id,
                environment_id=environment_id,
                x=0.1, y=0.1, width=0.3, height=0.3,
                origin="detected", status="suggested",
            ))
        session.commit()

    summary_before = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert summary_before.status_code == 200
    assert summary_before.json()["pending_faces"] == 2
    assert summary_before.json()["without_date"] == 2

    result = client.patch(
        f"{MEDIA_URL}/bulk",
        json={"operation": "reopen_curation", "media_ids": ids},
        headers=headers,
    )
    assert result.status_code == 200, result.text
    assert result.json()["succeeded_count"] == 2, result.text

    with test_session_factory() as session:
        media_with_album = session.get(FotosMediaModel, ids[0])
        media_without_album = session.get(FotosMediaModel, ids[1])
        assert media_with_album.album_id == album_id
        assert media_without_album.album_id is None
        assert media_with_album.curation_completed is False
        assert media_without_album.curation_completed is False
        assert media_with_album.audit_returned_to_curation is True
        assert media_without_album.audit_returned_to_curation is True
        assert session.query(FotosFaceModel).filter(
            FotosFaceModel.media_id.in_(ids),
            FotosFaceModel.status == "suggested",
        ).count() == 2

    summary_after = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert summary_after.status_code == 200
    assert summary_after.json()["pending_faces"] == 0
    assert summary_after.json()["without_date"] == 0

    pending_curation = client.get(
        "/api/fotos/curation/media",
        params={"environment_id": environment_id, "completion_status": "pending"},
        headers=headers,
    )
    assert pending_curation.status_code == 200, pending_curation.text
    assert set(ids).issubset({
        media["id"] for media in pending_curation.json()["items"]
    })


def test_audit_excludes_uncataloged_photographs_still_in_curation(
    client, media_context,
):
    """Foto sem álbum e sem curadoria concluída não é catalogada."""
    _, _, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
        content=create_test_jpeg(width=41, height=28),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    assert client.post(
        f"{MEDIA_URL}/{media_id}/process", headers=headers
    ).status_code == 200

    summary = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert summary.status_code == 200
    assert summary.json()["without_date"] == 0


def test_audit_finds_legacy_album_face_suggestions_and_hides_after_requeue(
    client, media_context, test_session_factory,
):
    """Foto legada no álbum, sem marcador de conclusão, ainda é auditável."""
    from deja_platform_api.fotos.media.models import FotosMediaModel

    org_id, tenant_id, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(width=43, height=31),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    assert client.post(
        f"{MEDIA_URL}/{media_id}/process", headers=headers
    ).status_code == 200
    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media.curation_completed is False
        session.add(FotosFaceModel(
            id=str(uuid4()),
            media_id=media_id,
            organization_id=org_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            x=0.1, y=0.1, width=0.3, height=0.3,
            origin="detected", status="suggested",
        ))
        session.commit()

    params = {"environment_id": environment_id}
    before = client.get(
        f"{MEDIA_URL}/audit/summary", params=params, headers=headers
    )
    assert before.status_code == 200, before.text
    assert before.json()["pending_faces"] == 1

    moved = client.patch(
        f"{MEDIA_URL}/bulk",
        json={"operation": "reopen_curation", "media_ids": [media_id]},
        headers=headers,
    )
    assert moved.status_code == 200, moved.text
    assert moved.json()["succeeded_count"] == 1, moved.text

    after = client.get(
        f"{MEDIA_URL}/audit/summary", params=params, headers=headers
    )
    assert after.status_code == 200
    assert after.json()["pending_faces"] == 0
    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media.album_id == album_id
        assert media.audit_returned_to_curation is True

    complete = client.post(
        f"/api/fotos/curation/media/{media_id}/completion",
        params={"completed": "true"},
        headers=headers,
    )
    assert complete.status_code == 200, complete.text
    restored = client.get(
        f"{MEDIA_URL}/audit/summary", params=params, headers=headers
    )
    assert restored.status_code == 200
    # Sugestões remanescentes ainda são encontradas pela Auditoria
    # caso não tenham sido confirmadas durante a revisão.
    assert restored.json()["pending_faces"] == 1
    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media.audit_returned_to_curation is False


def test_audit_rejects_unknown_category(client, media_context):
    _, _, environment_id, _, headers = media_context
    response = client.get(
        f"{MEDIA_URL}/audit/media",
        params={"environment_id": environment_id, "category": "unknown_faces"},
        headers=headers,
    )
    assert response.status_code == 422


def test_audit_filters_out_unprocessed_photographs(
    client, media_context, test_session_factory,
):
    from deja_platform_api.fotos.media.models import FotosMediaModel

    _, _, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(width=27, height=29),
    )
    assert uploaded.status_code == 201

    # TestClient já executou o processamento em segundo plano.
    # Simulamos explicitamente uma fotografia ainda não processada.
    with test_session_factory() as session:
        media = session.get(FotosMediaModel, uploaded.json()["id"])
        assert media is not None
        media.processing_status = "received"
        session.commit()

    response = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["without_date"] == 0


def test_audit_corrects_time_without_moving_existing_derivatives(
    client, media_context,
):
    """Data no mesmo mês: atualiza metadados sem renomear os derivados."""
    _, _, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(
            width=36,
            height=28,
            original_date=datetime(2020, 4, 26, 0, 0),
        ),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    assert client.post(
        f"{MEDIA_URL}/{media_id}/process", headers=headers
    ).status_code == 200
    assert client.get(
        f"{MEDIA_URL}/{media_id}/thumbnail", headers=headers
    ).status_code == 200

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_original_date",
            "media_ids": [media_id],
            "original_date": "2020-04-26T12:00:00",
            "original_date_precision": "datetime",
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["succeeded_count"] == 1, response.text
    media = response.json()["results"][0]["media"]
    assert media["original_date"] == "2020-04-26T12:00:00"
    assert media["original_date_precision"] == "datetime"
    assert media["album_id"] == album_id
    assert client.get(
        f"{MEDIA_URL}/{media_id}/thumbnail", headers=headers
    ).status_code == 200
    assert client.get(
        f"{MEDIA_URL}/{media_id}/preview", headers=headers
    ).status_code == 200

    summary = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert summary.status_code == 200
    assert summary.json()["without_time"] == 0


def test_audit_can_complete_known_time_without_removing_album(
    client, media_context
):
    _, _, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client, environment_id=environment_id,
        album_id=album_id, headers=headers,
        content=create_test_jpeg(width=37, height=23),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    assert client.post(f"{MEDIA_URL}/{media_id}/process", headers=headers).status_code == 200

    first = client.patch(
        f"{MEDIA_URL}/{media_id}/original-date",
        json={
            "original_date": "1992-05-19T12:00:00",
            "original_date_precision": "date",
        },
        headers=headers,
    )
    assert first.status_code == 200, first.text
    assert first.json()["original_date_precision"] == "date"

    second = client.patch(
        f"{MEDIA_URL}/{media_id}/original-date",
        json={
            "original_date": "1992-05-19T14:30:00",
            "original_date_precision": "datetime",
        },
        headers=headers,
    )
    assert second.status_code == 200, second.text
    assert second.json()["original_date_precision"] == "datetime"
    assert second.json()["album_id"] == album_id

    summary = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert summary.status_code == 200, summary.text
    assert summary.json()["without_time"] == 0
    assert summary.json()["without_album"] == 0


def test_audit_verify_date_clears_unverified_category(
    client, media_context, test_session_factory
):
    _, _, environment_id, album_id, headers = media_context
    uploaded = upload_image(
        client, environment_id=environment_id,
        album_id=album_id, headers=headers,
        content=create_test_jpeg(
            width=39, height=26,
            original_date=datetime(2006, 2, 12, 11, 15),
        ),
    )
    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    assert client.post(f"{MEDIA_URL}/{media_id}/process", headers=headers).status_code == 200

    mark_audit_ready(test_session_factory, media_id)

    before = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert before.status_code == 200
    assert before.json()["unverified_dates"] == 1

    result = client.patch(
        f"{MEDIA_URL}/bulk",
        json={"operation": "verify_original_date", "media_ids": [media_id]},
        headers=headers,
    )
    assert result.status_code == 200, result.text
    assert result.json()["succeeded_count"] == 1

    after = client.get(
        f"{MEDIA_URL}/audit/summary",
        params={"environment_id": environment_id},
        headers=headers,
    )
    assert after.status_code == 200
    assert after.json()["unverified_dates"] == 0
