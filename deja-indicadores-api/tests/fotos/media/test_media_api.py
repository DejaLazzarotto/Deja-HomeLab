import subprocess
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.media import (
    derivative_service as derivative_service_module,
)
from deja_indicadores_api.fotos.media.derivative_models import (
    FotosMediaDerivativeModel,
)
from deja_indicadores_api.fotos.media.image_derivatives import (
    FotosImageDerivativeError,
)
from deja_indicadores_api.fotos.media.models import FotosMediaModel
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


def create_test_jpeg(
    *,
    width: int = 16,
    height: int = 12,
) -> bytes:
    """Cria uma imagem JPEG real para os testes."""

    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
    )

    image.save(
        buffer,
        format="JPEG",
    )

    return buffer.getvalue()


def create_test_mp4(
    *,
    width: int = 16,
    height: int = 12,
    duration_seconds: float = 1.0,
) -> bytes:
    """Cria um vídeo MP4 real para os testes usando FFmpeg."""

    with tempfile.TemporaryDirectory() as temporary_directory:
        output_path = Path(temporary_directory) / "video.mp4"

        command = [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            (f"color=c=black:s={width}x{height}:d={duration_seconds}"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            "-y",
            str(output_path),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return output_path.read_bytes()


def upload_image(
    client: TestClient,
    *,
    environment_id: str,
    album_id: str | None,
    headers: Mapping[str, str],
    file_name: str = "foto.jpg",
    content: bytes | None = None,
    content_type: str = "image/jpeg",
):
    """Envia uma imagem de teste."""

    data = {
        "environment_id": environment_id,
    }

    if album_id is not None:
        data["album_id"] = album_id

    if content is None:
        content = create_test_jpeg()

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


def upload_video(
    client: TestClient,
    *,
    environment_id: str,
    album_id: str | None,
    headers: Mapping[str, str],
    file_name: str = "video.mp4",
    content: bytes | None = None,
):
    """Envia um vídeo de teste."""

    data = {
        "environment_id": environment_id,
    }

    if album_id is not None:
        data["album_id"] = album_id

    if content is None:
        content = create_test_mp4()

    return client.post(
        MEDIA_URL,
        data=data,
        files={
            "file": (
                file_name,
                content,
                "video/mp4",
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

    content = create_test_jpeg(
        width=16,
        height=12,
    )

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
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
    assert body["file_size"] == len(content)
    assert len(body["checksum_sha256"]) == 64
    assert body["processing_status"] == "received"
    assert body["width"] == 16
    assert body["height"] == 12
    assert body["duration_seconds"] is None
    assert body["original_date"] is None
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
    assert original_path.read_bytes() == content


def test_upload_video_extracts_metadata(
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
    """Valida vídeo real e extrai seus metadados."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_mp4(
        width=16,
        height=12,
        duration_seconds=1.0,
    )

    response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["organization_id"] == organization_id
    assert body["tenant_id"] == tenant_id
    assert body["environment_id"] == environment_id
    assert body["album_id"] == album_id
    assert body["original_name"] == "video.mp4"
    assert body["media_type"] == "video"
    assert body["content_type"] == "video/mp4"
    assert body["file_extension"] == ".mp4"
    assert body["file_size"] == len(content)
    assert len(body["checksum_sha256"]) == 64
    assert body["processing_status"] == "received"
    assert body["width"] == 16
    assert body["height"] == 12
    assert body["original_date"] is None
    assert body["view_count"] == 0
    assert body["deleted_at"] is None

    duration = body["duration_seconds"]

    assert duration is not None
    assert 0.9 <= duration <= 1.1

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / body["id"]
        / "original.mp4"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == content


def test_process_image_creates_thumbnail_and_preview(
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
    """Gera thumbnail e preview preservando o original."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=2000,
        height=1000,
    )

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["processing_status"] == "ready"
    assert body["processing_error"] is None

    base_path = test_settings.uploads_dir / "fotos" / organization_id / tenant_id / environment_id

    original_path = base_path / "originals" / created["id"] / "original.jpg"

    thumbnail_path = base_path / "derivatives" / created["id"] / "thumbnail.webp"

    preview_path = base_path / "derivatives" / created["id"] / "preview.webp"

    assert original_path.is_file()
    assert original_path.read_bytes() == content

    assert thumbnail_path.is_file()
    assert preview_path.is_file()

    with Image.open(thumbnail_path) as thumbnail:
        assert thumbnail.format == "WEBP"
        assert thumbnail.size == (320, 160)

    with Image.open(preview_path) as preview:
        assert preview.format == "WEBP"
        assert preview.size == (1600, 800)


def test_process_video_creates_poster(
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
    """Gera poster WebP de vídeo preservando o original."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_mp4(
        width=640,
        height=360,
        duration_seconds=2.0,
    )

    upload_response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["processing_status"] == "ready"
    assert body["processing_error"] is None

    base_path = test_settings.uploads_dir / "fotos" / organization_id / tenant_id / environment_id

    original_path = base_path / "originals" / created["id"] / "original.mp4"

    poster_path = base_path / "derivatives" / created["id"] / "poster.webp"

    assert original_path.is_file()
    assert original_path.read_bytes() == content

    assert poster_path.is_file()

    with Image.open(poster_path) as poster:
        assert poster.format == "WEBP"
        assert poster.size == (640, 360)


def test_get_thumbnail_and_preview(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Retorna os derivados WebP após o processamento."""

    _, _, environment_id, album_id, headers = media_context

    content = create_test_jpeg(
        width=2000,
        height=1000,
    )

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    process_response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert process_response.status_code == 200

    thumbnail_response = client.get(
        f"{MEDIA_URL}/{created['id']}/thumbnail",
        headers=headers,
    )

    assert thumbnail_response.status_code == 200
    assert thumbnail_response.headers["content-type"] == "image/webp"

    with Image.open(BytesIO(thumbnail_response.content)) as thumbnail:
        assert thumbnail.format == "WEBP"
        assert thumbnail.size == (320, 160)

    preview_response = client.get(
        f"{MEDIA_URL}/{created['id']}/preview",
        headers=headers,
    )

    assert preview_response.status_code == 200
    assert preview_response.headers["content-type"] == "image/webp"

    with Image.open(BytesIO(preview_response.content)) as preview:
        assert preview.format == "WEBP"
        assert preview.size == (1600, 800)


def test_get_video_poster(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Retorna o poster WebP após o processamento do vídeo."""

    _, _, environment_id, album_id, headers = media_context

    content = create_test_mp4(
        width=640,
        height=360,
        duration_seconds=2.0,
    )

    upload_response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    process_response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert process_response.status_code == 200

    poster_response = client.get(
        f"{MEDIA_URL}/{created['id']}/poster",
        headers=headers,
    )

    assert poster_response.status_code == 200
    assert poster_response.headers["content-type"] == "image/webp"

    with Image.open(BytesIO(poster_response.content)) as poster:
        assert poster.format == "WEBP"
        assert poster.size == (640, 360)


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

    linked_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="vinculada.jpg",
    )

    assert linked_response.status_code == 201

    linked = linked_response.json()

    unlinked_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=None,
        headers=headers,
        file_name="sem-album.jpg",
    )

    assert unlinked_response.status_code == 201

    response = client.get(
        MEDIA_URL,
        params={
            "album_id": album_id,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert [media["id"] for media in response.json()] == [
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

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert create_response.status_code == 201

    created = create_response.json()

    response = client.get(
        f"{MEDIA_URL}/{created['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created["id"]
    assert body["organization_id"] == created["organization_id"]
    assert body["tenant_id"] == created["tenant_id"]
    assert body["environment_id"] == created["environment_id"]
    assert body["album_id"] == created["album_id"]
    assert body["original_name"] == created["original_name"]
    assert body["media_type"] == created["media_type"]
    assert body["content_type"] == created["content_type"]
    assert body["file_extension"] == created["file_extension"]
    assert body["file_size"] == created["file_size"]
    assert body["checksum_sha256"] == created["checksum_sha256"]
    assert body["processing_status"] == "ready"
    assert body["processing_error"] is None


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

    content = create_test_jpeg()

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert create_response.status_code == 201

    created = create_response.json()

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

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert create_response.status_code == 201

    created = create_response.json()

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
    assert get_response.json()["error"] == "fotos_media_not_found"


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


def test_upload_media_rejects_invalid_image_content(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita arquivo falso mesmo com MIME de imagem permitido."""

    _, _, environment_id, album_id, headers = media_context

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=b"isto-nao-e-um-jpeg",
        content_type="image/jpeg",
    )

    assert response.status_code == 422
    assert response.json()["error"] == "fotos_media_invalid_content"


def test_upload_media_rejects_invalid_video_content(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita arquivo falso mesmo com MIME de vídeo permitido."""

    _, _, environment_id, album_id, headers = media_context

    response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=b"isto-nao-e-um-video-mp4",
    )

    assert response.status_code == 422
    assert response.json()["error"] == "fotos_media_invalid_content"


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
    assert response.json()["error"] == "fotos_media_empty_file"


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
    assert response.json()["error"] == "fotos_media_not_found"


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


def test_process_video_creates_and_returns_preview(
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
    """Gera preview MP4 reduzido e o disponibiliza pela API."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_mp4(
        width=1920,
        height=1080,
        duration_seconds=2.0,
    )

    upload_response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    process_response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert process_response.status_code == 200
    assert process_response.json()["processing_status"] == "ready"

    preview_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / created["id"]
        / "preview.mp4"
    )

    assert preview_path.is_file()
    assert preview_path.stat().st_size > 0

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            str(preview_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert probe.stdout.strip() == "1280x720"

    preview_response = client.get(
        f"{MEDIA_URL}/{created['id']}/preview",
        headers=headers,
    )

    assert preview_response.status_code == 200
    assert preview_response.headers["content-type"] == "video/mp4"
    assert preview_response.content == preview_path.read_bytes()


def test_list_media_derivatives(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista os metadados públicos dos derivados sem expor storage_key."""

    _, _, environment_id, album_id, headers = media_context

    content = create_test_jpeg(
        width=2000,
        height=1000,
    )

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    process_response = client.post(
        f"{MEDIA_URL}/{created['id']}/process",
        headers=headers,
    )

    assert process_response.status_code == 200

    response = client.get(
        f"{MEDIA_URL}/{created['id']}/derivatives",
        headers=headers,
    )

    assert response.status_code == 200

    derivatives = response.json()

    assert [derivative["derivative_type"] for derivative in derivatives] == [
        "preview",
        "thumbnail",
    ]

    for derivative in derivatives:
        assert "id" in derivative
        assert "content_type" in derivative
        assert "file_extension" in derivative
        assert "file_size" in derivative
        assert "width" in derivative
        assert "height" in derivative
        assert "created_at" in derivative
        assert "storage_key" not in derivative


def set_media_processing_state(
    test_session_factory: sessionmaker[Session],
    media_id: str,
    *,
    status: str,
    error: str | None = None,
    updated_at: datetime | None = None,
) -> None:
    """Prepara um estado operacional especifico para a midia."""

    with test_session_factory() as session:
        media = session.get(FotosMediaModel, media_id)

        assert media is not None

        media.processing_status = status
        media.processing_error = error

        if updated_at is not None:
            media.updated_at = updated_at

        session.commit()


def test_process_ready_media_is_idempotent(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Reutiliza os mesmos derivados quando a midia ja esta pronta."""

    _, _, environment_id, album_id, headers = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    before_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert before_response.status_code == 200

    before = before_response.json()

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None

    after_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert after_response.status_code == 200
    assert after_response.json() == before


def test_process_ready_media_recovers_missing_derivative_file(
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
    """Regenera um arquivo ausente sem duplicar seu registro."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(
            width=2000,
            height=1000,
        ),
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    before_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert before_response.status_code == 200

    before = before_response.json()
    before_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in before
    }

    thumbnail_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / media_id
        / "thumbnail.webp"
    )

    assert thumbnail_path.is_file()

    thumbnail_path.unlink()

    assert not thumbnail_path.exists()

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None
    assert thumbnail_path.is_file()
    assert thumbnail_path.stat().st_size > 0

    with Image.open(thumbnail_path) as thumbnail:
        thumbnail.load()

        assert thumbnail.format == "WEBP"
        assert thumbnail.size == (320, 160)

    after_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert after_response.status_code == 200

    after = after_response.json()
    after_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in after
    }

    assert len(after) == 2
    assert after_ids == before_ids


def test_process_ready_video_recovers_corrupted_preview(
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
    """Regenera um preview MP4 corrompido preservando seu registro."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    upload_response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_mp4(
            width=640,
            height=360,
            duration_seconds=1.0,
        ),
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    before_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert before_response.status_code == 200

    before = before_response.json()
    before_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in before
    }

    preview_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / media_id
        / "preview.mp4"
    )

    assert preview_path.is_file()

    preview_size = preview_path.stat().st_size

    assert preview_size > 0

    preview_path.write_bytes(
        b"\x00" * preview_size
    )

    assert preview_path.stat().st_size == preview_size

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None
    assert preview_path.is_file()
    assert preview_path.stat().st_size > 0

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            str(preview_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert probe.stdout.strip() == "640x360"

    after_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert after_response.status_code == 200

    after = after_response.json()
    after_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in after
    }

    assert len(after) == 2
    assert after_ids == before_ids


def test_process_ready_media_replaces_orphan_file(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_session_factory: sessionmaker[Session],
    test_settings: Settings,
) -> None:
    """Substitui arquivo órfão e recria seu registro de derivado."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(
            width=2000,
            height=1000,
        ),
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    before_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert before_response.status_code == 200

    before = before_response.json()
    preview_before = next(
        derivative
        for derivative in before
        if derivative["derivative_type"] == "preview"
    )

    preview_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / media_id
        / "preview.webp"
    )

    assert preview_path.is_file()

    with test_session_factory() as session:
        derivative = session.get(
            FotosMediaDerivativeModel,
            preview_before["id"],
        )

        assert derivative is not None

        session.delete(derivative)
        session.commit()

    preview_path.write_bytes(
        b"orphan-derivative"
    )

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None

    with Image.open(preview_path) as preview:
        preview.load()

        assert preview.format == "WEBP"
        assert preview.size == (1600, 800)

    after_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert after_response.status_code == 200

    after = after_response.json()
    preview_after = next(
        derivative
        for derivative in after
        if derivative["derivative_type"] == "preview"
    )

    assert len(after) == 2
    assert preview_after["id"] != preview_before["id"]


def test_processing_failure_preserves_recovered_derivative(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserva derivado recuperado quando o seguinte falha."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=create_test_jpeg(
            width=2000,
            height=1000,
        ),
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    before_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert before_response.status_code == 200

    before = before_response.json()
    before_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in before
    }

    derivatives_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / media_id
    )
    thumbnail_path = derivatives_path / "thumbnail.webp"
    preview_path = derivatives_path / "preview.webp"

    assert thumbnail_path.is_file()
    assert preview_path.is_file()

    thumbnail_path.unlink()
    preview_path.unlink()

    original_generate = (
        derivative_service_module.generate_image_derivative
    )

    def generate_with_preview_failure(
        source_path: Path,
        destination_path: Path,
        *,
        derivative_type: str,
    ):
        if derivative_type == "preview":
            raise FotosImageDerivativeError(
                "Falha simulada no preview."
            )

        return original_generate(
            source_path,
            destination_path,
            derivative_type=derivative_type,
        )

    monkeypatch.setattr(
        derivative_service_module,
        "generate_image_derivative",
        generate_with_preview_failure,
    )

    with pytest.raises(
        FotosImageDerivativeError,
        match="Falha simulada no preview",
    ):
        client.post(
            f"{MEDIA_URL}/{media_id}/process",
            headers=headers,
        )

    assert thumbnail_path.is_file()
    assert thumbnail_path.stat().st_size > 0
    assert not preview_path.exists()

    after_response = client.get(
        f"{MEDIA_URL}/{media_id}/derivatives",
        headers=headers,
    )

    assert after_response.status_code == 200

    after = after_response.json()
    after_ids = {
        derivative["derivative_type"]: derivative["id"]
        for derivative in after
    }

    assert len(after) == 2
    assert after_ids == before_ids

    media_response = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )

    assert media_response.status_code == 200
    assert media_response.json()["processing_status"] == "failed"
    assert (
        media_response.json()["processing_error"]
        == "Falha simulada no preview."
    )


def test_process_failed_media_retries_successfully(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_session_factory: sessionmaker[Session],
) -> None:
    """Permite retry de uma midia com processamento anterior falho."""

    _, _, environment_id, album_id, headers = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    set_media_processing_state(
        test_session_factory,
        media_id,
        status="failed",
        error="Falha simulada.",
    )

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None


def test_process_recent_processing_media_returns_conflict(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_session_factory: sessionmaker[Session],
) -> None:
    """Bloqueia nova tentativa enquanto o processamento esta ativo."""

    _, _, environment_id, album_id, headers = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]

    set_media_processing_state(
        test_session_factory,
        media_id,
        status="processing",
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "fotos_media_already_processing"

    get_response = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["processing_status"] == "processing"


def test_process_stale_processing_media_recovers(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_session_factory: sessionmaker[Session],
    test_settings: Settings,
) -> None:
    """Recupera uma tentativa abandonada apos o limite configurado."""

    _, _, environment_id, album_id, headers = media_context

    upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
    )

    assert upload_response.status_code == 201

    media_id = upload_response.json()["id"]
    stale_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(
        minutes=(
            test_settings.fotos_media_processing_timeout_minutes
            + 1
        ),
    )

    set_media_processing_state(
        test_session_factory,
        media_id,
        status="processing",
        updated_at=stale_at,
    )

    response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "ready"
    assert response.json()["processing_error"] is None
