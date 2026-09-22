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
    SECOND_ALBUM,
    create_album,
)
from tests.module_management.test_authenticated_modules_api import (
    configure_organization_modules,
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

    configure_organization_modules(
        client,
        str(organization["id"]),
        {
            "fotos",
        },
    )

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
    original_date: datetime | None = None,
) -> bytes:
    """Cria uma imagem JPEG real para os testes."""

    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
    )

    exif = Image.Exif()

    if original_date is not None:
        exif[36867] = original_date.strftime(
            "%Y:%m:%d %H:%M:%S",
        )

    image.save(
        buffer,
        format="JPEG",
        exif=exif,
    )

    return buffer.getvalue()


def create_test_gif(
    *,
    width: int = 16,
    height: int = 12,
) -> bytes:
    """Cria um GIF animado real para os testes."""

    buffer = BytesIO()

    first_frame = Image.new(
        "RGB",
        (width, height),
        color="red",
    )
    second_frame = Image.new(
        "RGB",
        (width, height),
        color="blue",
    )

    first_frame.save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=[second_frame],
        duration=100,
        loop=0,
    )

    return buffer.getvalue()


def create_test_bmp(
    *,
    width: int = 16,
    height: int = 12,
) -> bytes:
    """Cria uma imagem BMP real para os testes."""

    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
        color="green",
    )

    image.save(
        buffer,
        format="BMP",
    )

    return buffer.getvalue()


def create_test_webp(
    *,
    width: int = 16,
    height: int = 12,
) -> bytes:
    """Cria uma imagem WebP real para os testes."""

    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
        color="purple",
    )

    image.save(
        buffer,
        format="WEBP",
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


def create_test_legacy_video(
    *,
    file_extension: str,
    video_codec: str,
    width: int = 16,
    height: int = 12,
    duration_seconds: float = 1.0,
) -> bytes:
    """Cria um vídeo legado real para os testes."""

    with tempfile.TemporaryDirectory() as temporary_directory:
        output_path = Path(temporary_directory) / f"video{file_extension}"

        command = [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            (f"color=c=black:s={width}x{height}:d={duration_seconds}"),
            "-c:v",
            video_codec,
            "-pix_fmt",
            "yuv420p",
            "-an",
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
    content_type: str = "video/mp4",
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
    assert body["source_content_type"] == "image/jpeg"
    assert body["source_file_extension"] == ".jpg"
    assert body["source_file_size"] == len(content)
    assert len(body["source_checksum_sha256"]) == 64
    assert body["media_type"] == "image"
    assert body["content_type"] == "image/jpeg"
    assert body["file_extension"] == ".jpg"
    assert body["file_size"] == len(content)
    assert len(body["checksum_sha256"]) == 64
    assert body["source_checksum_sha256"] == body["checksum_sha256"]
    assert body["was_converted"] is False
    assert body["processing_status"] == "received"
    assert body["width"] == 16
    assert body["height"] == 12
    assert body["duration_seconds"] is None
    assert body["original_date"] is None
    assert body["original_date_source"] is None
    assert body["original_date_verified"] is False
    assert body["original_date_conflict"] is False
    assert body["view_count"] == 0
    assert body["deleted_at"] is None

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / body["id"]
        / "original.jpg"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == content


def test_upload_media_stores_image_by_embedded_year_and_month(
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
    """Armazena imagem com data EXIF no diretório cronológico."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    original_date = datetime(
        2021,
        4,
        9,
        18,
        30,
        15,
    )

    content = create_test_jpeg(
        width=20,
        height=15,
        original_date=original_date,
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

    assert body["original_date"] == "2021-04-09T18:30:15"
    assert body["original_date_source"] == "embedded_metadata"
    assert body["original_date_verified"] is False
    assert body["original_date_conflict"] is False
    assert body["was_converted"] is False

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2021"
        / "04"
        / body["id"]
        / "original.jpg"
    )

    staging_directory = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / ".staging"
        / body["id"]
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == content
    assert not staging_directory.exists()


def test_upload_gif_preserves_animated_original(
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
    """Preserva integralmente o GIF animado recebido."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_gif(
        width=20,
        height=15,
    )

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="animacao.gif",
        content=content,
        content_type="image/gif",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["original_name"] == "animacao.gif"
    assert body["source_content_type"] == "image/gif"
    assert body["source_file_extension"] == ".gif"
    assert body["source_file_size"] == len(content)
    assert body["content_type"] == "image/gif"
    assert body["file_extension"] == ".gif"
    assert body["file_size"] == len(content)
    assert body["source_checksum_sha256"] == body["checksum_sha256"]
    assert body["was_converted"] is False
    assert body["original_date"] is None

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / body["id"]
        / "original.gif"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == content

    with Image.open(original_path) as stored:
        assert stored.format == "GIF"
        assert stored.size == (20, 15)
        assert stored.n_frames == 2


def test_upload_bmp_converts_managed_original_to_png(
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
    """Converte BMP para PNG preservando os metadados da fonte."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_bmp(
        width=20,
        height=15,
    )

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="foto-legada.bmp",
        content=content,
        content_type="image/bmp",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["original_name"] == "foto-legada.bmp"
    assert body["source_content_type"] == "image/bmp"
    assert body["source_file_extension"] == ".bmp"
    assert body["source_file_size"] == len(content)
    assert len(body["source_checksum_sha256"]) == 64

    assert body["media_type"] == "image"
    assert body["content_type"] == "image/png"
    assert body["file_extension"] == ".png"
    assert body["file_size"] > 0
    assert len(body["checksum_sha256"]) == 64
    assert body["source_checksum_sha256"] != body["checksum_sha256"]
    assert body["was_converted"] is True
    assert body["width"] == 20
    assert body["height"] == 15

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / body["id"]
        / "original.png"
    )

    assert original_path.is_file()
    assert original_path.stat().st_size == body["file_size"]
    assert original_path.read_bytes() != content

    with Image.open(original_path) as stored:
        assert stored.format == "PNG"
        assert stored.size == (20, 15)


def test_upload_webp_converts_managed_original_to_png(
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
    """Converte WebP para PNG preservando os metadados da fonte."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_webp(
        width=20,
        height=15,
    )

    response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="foto-web.webp",
        content=content,
        content_type="image/webp",
    )

    assert response.status_code == 201

    body = response.json()

    assert body["original_name"] == "foto-web.webp"
    assert body["source_content_type"] == "image/webp"
    assert body["source_file_extension"] == ".webp"
    assert body["source_file_size"] == len(content)
    assert body["content_type"] == "image/png"
    assert body["file_extension"] == ".png"
    assert body["was_converted"] is True
    assert body["width"] == 20
    assert body["height"] == 15
    assert body["source_checksum_sha256"] != body["checksum_sha256"]

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / body["id"]
        / "original.png"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() != content

    with Image.open(original_path) as stored:
        assert stored.format == "PNG"
        assert stored.size == (20, 15)


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
        / "sem-data"
        / body["id"]
        / "original.mp4"
    )

    assert original_path.is_file()
    assert original_path.read_bytes() == content


@pytest.mark.parametrize(
    (
        "source_extension",
        "source_content_type",
        "source_video_codec",
    ),
    [
        (
            ".mov",
            "video/quicktime",
            "libx264",
        ),
        (
            ".mpg",
            "video/mpeg",
            "mpeg2video",
        ),
    ],
)
def test_upload_legacy_video_converts_original_to_mp4(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
    source_extension: str,
    source_content_type: str,
    source_video_codec: str,
) -> None:
    """Converte vídeo legado para MP4 durante o processamento."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_legacy_video(
        file_extension=source_extension,
        video_codec=source_video_codec,
        width=20,
        height=16,
    )

    upload_response = upload_video(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name=f"video-legado{source_extension}",
        content=content,
        content_type=source_content_type,
    )

    assert upload_response.status_code == 201

    created = upload_response.json()

    assert created["source_content_type"] == source_content_type
    assert created["source_file_extension"] == source_extension
    assert created["source_file_size"] == len(content)
    assert created["was_converted"] is False

    response = client.get(
        f"{MEDIA_URL}/{created['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["processing_status"] == "ready"
    assert body["processing_error"] is None
    assert body["source_content_type"] == source_content_type
    assert body["source_file_extension"] == source_extension
    assert body["source_file_size"] == len(content)
    assert body["source_checksum_sha256"] == (created["source_checksum_sha256"])

    assert body["content_type"] == "video/mp4"
    assert body["file_extension"] == ".mp4"
    assert body["file_size"] > 0
    assert body["was_converted"] is True
    assert body["width"] == 20
    assert body["height"] == 16
    assert body["checksum_sha256"] != body["source_checksum_sha256"]

    media_directory = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / body["id"]
    )

    source_path = media_directory / f"original{source_extension}"
    normalized_path = media_directory / "normalized.mp4"

    assert not source_path.exists()
    assert normalized_path.is_file()
    assert normalized_path.stat().st_size == body["file_size"]

    download_response = client.get(
        f"{MEDIA_URL}/{body['id']}/original",
        headers=headers,
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "video/mp4"
    assert "video-legado.mp4" in (download_response.headers["content-disposition"])
    assert download_response.content == normalized_path.read_bytes()


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

    original_path = base_path / "originals" / "sem-data" / created["id"] / "original.jpg"

    thumbnail_path = base_path / "derivatives" / "sem-data" / created["id"] / "thumbnail.webp"

    preview_path = base_path / "derivatives" / "sem-data" / created["id"] / "preview.webp"

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

    original_path = base_path / "originals" / "sem-data" / created["id"] / "original.mp4"

    poster_path = base_path / "derivatives" / "sem-data" / created["id"] / "poster.webp"

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


def test_missing_video_poster_returns_not_found(
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
    """Retorna 404 quando o poster físico não existe."""

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

    media_id = upload_response.json()["id"]

    process_response = client.post(
        f"{MEDIA_URL}/{media_id}/process",
        headers=headers,
    )

    assert process_response.status_code == 200

    base_path = test_settings.uploads_dir / "fotos" / organization_id / tenant_id / environment_id

    poster_path = base_path / "derivatives" / "sem-data" / media_id / "poster.webp"

    assert poster_path.is_file()

    poster_path.unlink()

    response = client.get(
        f"{MEDIA_URL}/{media_id}/poster",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "fotos_media_derivative_not_found"


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
        content=create_test_jpeg(
            width=17,
            height=13,
        ),
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

    payload = response.json()

    assert [media["id"] for media in payload["items"]] == [
        linked["id"],
    ]
    assert payload["page"] == 1
    assert payload["page_size"] == 50
    assert payload["total"] == 1
    assert payload["total_pages"] == 1


def test_list_media_paginates_results(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Retorna somente a página solicitada e informa os totais."""

    _, _, environment_id, album_id, headers = media_context

    created_ids = []

    for day in (1, 2, 3):
        response = upload_image(
            client,
            environment_id=environment_id,
            album_id=album_id,
            headers=headers,
            file_name=f"foto-{day}.jpg",
            content=create_test_jpeg(
                width=16 + day,
                height=12,
                original_date=datetime(
                    2024,
                    1,
                    day,
                    12,
                ),
            ),
        )

        assert response.status_code == 201

        created_ids.append(response.json()["id"])

    first_page_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "page": 1,
            "page_size": 2,
        },
        headers=headers,
    )

    assert first_page_response.status_code == 200

    first_page = first_page_response.json()

    assert [item["id"] for item in first_page["items"]] == [
        created_ids[2],
        created_ids[1],
    ]
    assert first_page["page"] == 1
    assert first_page["page_size"] == 2
    assert first_page["total"] == 3
    assert first_page["total_pages"] == 2

    second_page_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "page": 2,
            "page_size": 2,
        },
        headers=headers,
    )

    assert second_page_response.status_code == 200

    second_page = second_page_response.json()

    assert [item["id"] for item in second_page["items"]] == [
        created_ids[0],
    ]
    assert second_page["page"] == 2
    assert second_page["page_size"] == 2
    assert second_page["total"] == 3
    assert second_page["total_pages"] == 2


def test_list_media_filters_by_original_date_and_curation_flags(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Filtra mídias por data original e pelos estados de curadoria."""

    _, _, environment_id, album_id, headers = media_context

    january_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="janeiro-2023.jpg",
        content=create_test_jpeg(
            width=21,
            height=13,
            original_date=datetime(
                2023,
                1,
                15,
                10,
            ),
        ),
    )

    february_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="fevereiro-2024.jpg",
        content=create_test_jpeg(
            width=22,
            height=13,
            original_date=datetime(
                2024,
                2,
                20,
                11,
            ),
        ),
    )

    without_date_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="sem-data.jpg",
        content=create_test_jpeg(
            width=23,
            height=13,
        ),
    )

    converted_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="convertida.bmp",
        content=create_test_bmp(
            width=24,
            height=13,
        ),
        content_type="image/bmp",
    )

    assert january_response.status_code == 201
    assert february_response.status_code == 201
    assert without_date_response.status_code == 201
    assert converted_response.status_code == 201

    january_id = january_response.json()["id"]
    february_id = february_response.json()["id"]
    without_date_id = without_date_response.json()["id"]
    converted_id = converted_response.json()["id"]

    with test_session_factory() as session:
        january = session.get(
            FotosMediaModel,
            january_id,
        )
        february = session.get(
            FotosMediaModel,
            february_id,
        )

        assert january is not None
        assert february is not None

        january.original_date_verified = True
        february.original_date_conflict = True

        session.commit()

    year_month_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "original_year": 2024,
            "original_month": 2,
        },
        headers=headers,
    )

    assert year_month_response.status_code == 200
    assert [item["id"] for item in year_month_response.json()["items"]] == [february_id]

    interval_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "original_date_from": "2024-02-20T07:00:00-03:00",
            "original_date_to": "2024-02-20T09:00:00-03:00",
        },
        headers=headers,
    )

    assert interval_response.status_code == 200
    assert [item["id"] for item in interval_response.json()["items"]] == [february_id]

    without_date_filter_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "without_original_date": True,
        },
        headers=headers,
    )

    assert without_date_filter_response.status_code == 200
    assert {item["id"] for item in without_date_filter_response.json()["items"]} == {
        without_date_id,
        converted_id,
    }

    verified_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "original_date_verified": True,
        },
        headers=headers,
    )

    assert verified_response.status_code == 200
    assert [item["id"] for item in verified_response.json()["items"]] == [january_id]

    conflict_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "original_date_conflict": True,
        },
        headers=headers,
    )

    assert conflict_response.status_code == 200
    assert [item["id"] for item in conflict_response.json()["items"]] == [february_id]

    converted_filter_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
            "was_converted": True,
        },
        headers=headers,
    )

    assert converted_filter_response.status_code == 200
    assert [item["id"] for item in converted_filter_response.json()["items"]] == [converted_id]


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


def test_update_original_date_moves_original_and_preserves_derivatives(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
) -> None:
    """Move o original e mantém os derivados após confirmação manual."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=25,
        height=17,
    )

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="data-manual.jpg",
        content=content,
    )

    assert create_response.status_code == 201

    created = create_response.json()
    media_id = created["id"]

    old_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / media_id
        / "original.jpg"
    )

    new_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2020"
        / "05"
        / media_id
        / "original.jpg"
    )

    assert old_path.is_file()

    thumbnail_before = client.get(
        f"{MEDIA_URL}/{media_id}/thumbnail",
        headers=headers,
    )

    assert thumbnail_before.status_code == 200

    with test_session_factory() as session:
        media = session.get(
            FotosMediaModel,
            media_id,
        )

        assert media is not None

        media.original_date_conflict = True
        session.commit()

    response = client.patch(
        f"{MEDIA_URL}/{media_id}/original-date",
        json={
            "original_date": "2020-05-17T15:30:00-03:00",
        },
        headers=headers,
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["original_date"] == "2020-05-17T18:30:00"
    assert updated["original_date_source"] == "manual"
    assert updated["original_date_verified"] is True
    assert updated["original_date_conflict"] is False

    assert not old_path.exists()
    assert new_path.read_bytes() == content

    thumbnail_after = client.get(
        f"{MEDIA_URL}/{media_id}/thumbnail",
        headers=headers,
    )

    assert thumbnail_after.status_code == 200
    assert thumbnail_after.content == thumbnail_before.content

    with test_session_factory() as session:
        media = session.get(
            FotosMediaModel,
            media_id,
        )

        assert media is not None
        assert media.original_storage_key.endswith(f"/2020/05/{media_id}/original.jpg")


def test_update_original_date_in_same_month_keeps_storage_path(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
    test_settings: Settings,
) -> None:
    """Atualiza a data sem mover o original quando o mês não muda."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=26,
        height=17,
        original_date=datetime(
            2020,
            5,
            1,
            10,
        ),
    )

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="mesmo-mes.jpg",
        content=content,
    )

    assert create_response.status_code == 201

    media_id = create_response.json()["id"]

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2020"
        / "05"
        / media_id
        / "original.jpg"
    )

    with test_session_factory() as session:
        media = session.get(
            FotosMediaModel,
            media_id,
        )

        assert media is not None

        previous_storage_key = media.original_storage_key

    response = client.patch(
        f"{MEDIA_URL}/{media_id}/original-date",
        json={
            "original_date": "2020-05-20T14:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["original_date"] == "2020-05-20T14:00:00"
    assert response.json()["original_date_source"] == "manual"
    assert response.json()["original_date_verified"] is True
    assert original_path.read_bytes() == content

    with test_session_factory() as session:
        media = session.get(
            FotosMediaModel,
            media_id,
        )

        assert media is not None
        assert media.original_storage_key == previous_storage_key


def test_update_original_date_rejects_occupied_destination(
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
    """Não sobrescreve um destino físico já ocupado."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=27,
        height=17,
    )

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="conflito-destino.jpg",
        content=content,
    )

    assert create_response.status_code == 201

    media_id = create_response.json()["id"]

    old_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / media_id
        / "original.jpg"
    )

    occupied_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2021"
        / "06"
        / media_id
        / "original.jpg"
    )

    occupied_path.parent.mkdir(
        parents=True,
        exist_ok=False,
    )
    occupied_path.write_bytes(b"arquivo-preexistente")

    response = client.patch(
        f"{MEDIA_URL}/{media_id}/original-date",
        json={
            "original_date": "2021-06-10T12:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "fotos_media_storage_conflict"
    assert old_path.read_bytes() == content
    assert occupied_path.read_bytes() == b"arquivo-preexistente"


def test_media_role_permissions_match_reader_operator_and_manager(
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
    """Valida leitura, operação e curadoria conforme o papel."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        _administrator_headers,
    ) = media_context

    viewer = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="viewer.permissions.fotos.media@deja.com",
        role="viewer",
    )
    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )

    list_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
        },
        headers=viewer_headers,
    )

    assert list_response.status_code == 200, list_response.json()

    viewer_upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=viewer_headers,
        file_name="viewer-sem-permissao.jpg",
        content=create_test_jpeg(
            width=29,
            height=18,
        ),
    )

    assert viewer_upload_response.status_code == 403

    analyst = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="analyst.permissions.fotos.media@deja.com",
        role="analyst",
    )
    analyst_headers = authorization_headers(
        test_settings,
        analyst,
    )

    analyst_upload_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=analyst_headers,
        file_name="analyst-permitido.jpg",
        content=create_test_jpeg(
            width=31,
            height=19,
        ),
    )

    assert analyst_upload_response.status_code == 201

    media_id = analyst_upload_response.json()["id"]

    analyst_bulk_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [media_id],
        },
        headers=analyst_headers,
    )

    assert analyst_bulk_response.status_code == 403

    manager = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="manager.permissions.fotos.media@deja.com",
        role="manager",
    )
    manager_headers = authorization_headers(
        test_settings,
        manager,
    )

    manager_bulk_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [media_id],
        },
        headers=manager_headers,
    )

    assert manager_bulk_response.status_code == 200
    assert manager_bulk_response.json()["succeeded_count"] == 1
    assert manager_bulk_response.json()["failed_count"] == 0


def test_update_original_date_rejects_analyst(
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
    """Impede que analista confirme manualmente a data original."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        administrator_headers,
    ) = media_context

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=administrator_headers,
        file_name="sem-permissao.jpg",
        content=create_test_jpeg(
            width=28,
            height=17,
        ),
    )

    assert create_response.status_code == 201

    analyst = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="analyst.fotos.media@deja.com",
        role="analyst",
    )
    analyst_headers = authorization_headers(
        test_settings,
        analyst,
    )

    response = client.patch(
        (f"{MEDIA_URL}/{create_response.json()['id']}/original-date"),
        json={
            "original_date": "2022-07-10T12:00:00",
        },
        headers=analyst_headers,
    )

    assert response.status_code == 403


def test_bulk_set_original_date_moves_originals(
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
    """Aplica uma data manual e move todos os originais do lote."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    contents = [
        create_test_jpeg(
            width=31,
            height=17,
        ),
        create_test_jpeg(
            width=32,
            height=17,
        ),
    ]
    media_ids: list[str] = []

    for index, content in enumerate(contents):
        create_response = upload_image(
            client,
            environment_id=environment_id,
            album_id=album_id,
            headers=headers,
            file_name=f"lote-data-{index}.jpg",
            content=content,
        )

        assert create_response.status_code == 201

        media_id = create_response.json()["id"]
        media_ids.append(media_id)

        process_response = client.post(
            f"{MEDIA_URL}/{media_id}/process",
            headers=headers,
        )

        assert process_response.status_code == 200
        assert process_response.json()["processing_status"] == "ready"

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_original_date",
            "media_ids": media_ids,
            "original_date": "2024-03-10T12:00:00-03:00",
        },
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["operation"] == "set_original_date"
    assert result["requested_count"] == 2
    assert result["succeeded_count"] == 2
    assert result["failed_count"] == 0
    assert [item["media_id"] for item in result["results"]] == media_ids
    assert all(item["success"] for item in result["results"])
    assert all(
        item["media"]["original_date"] == "2024-03-10T15:00:00" for item in result["results"]
    )
    assert all(item["media"]["original_date_source"] == "manual" for item in result["results"])
    assert all(item["media"]["original_date_verified"] is True for item in result["results"])

    for media_id, content in zip(
        media_ids,
        contents,
        strict=True,
    ):
        old_path = (
            test_settings.uploads_dir
            / "fotos"
            / organization_id
            / tenant_id
            / environment_id
            / "originals"
            / "sem-data"
            / media_id
            / "original.jpg"
        )
        new_path = (
            test_settings.uploads_dir
            / "fotos"
            / organization_id
            / tenant_id
            / environment_id
            / "originals"
            / "2024"
            / "03"
            / media_id
            / "original.jpg"
        )

        old_derivatives_path = (
            test_settings.uploads_dir
            / "fotos"
            / organization_id
            / tenant_id
            / environment_id
            / "derivatives"
            / "sem-data"
            / media_id
        )
        new_derivatives_path = (
            test_settings.uploads_dir
            / "fotos"
            / organization_id
            / tenant_id
            / environment_id
            / "derivatives"
            / "2024"
            / "03"
            / media_id
        )

        assert not old_path.exists()
        assert new_path.read_bytes() == content
        assert not old_derivatives_path.exists()
        assert (new_derivatives_path / "thumbnail.webp").is_file()
        assert (new_derivatives_path / "preview.webp").is_file()

        thumbnail_response = client.get(
            f"{MEDIA_URL}/{media_id}/thumbnail",
            headers=headers,
        )

        assert thumbnail_response.status_code == 200
        assert thumbnail_response.headers["content-type"] == "image/webp"


def test_bulk_set_original_date_continues_after_storage_conflict(
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
    """Preserva a falha de um item e continua processando o lote."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    first_content = create_test_jpeg(
        width=33,
        height=17,
    )
    second_content = create_test_jpeg(
        width=34,
        height=17,
    )

    first_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="lote-conflito.jpg",
        content=first_content,
    )
    second_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="lote-sucesso.jpg",
        content=second_content,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    first_old_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / first_id
        / "original.jpg"
    )
    occupied_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2025"
        / "04"
        / first_id
        / "original.jpg"
    )
    second_new_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2025"
        / "04"
        / second_id
        / "original.jpg"
    )

    occupied_path.parent.mkdir(
        parents=True,
        exist_ok=False,
    )
    occupied_path.write_bytes(b"destino-ocupado")

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_original_date",
            "media_ids": [
                first_id,
                second_id,
            ],
            "original_date": "2025-04-20T10:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["requested_count"] == 2
    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1

    first_result = result["results"][0]
    second_result = result["results"][1]

    assert first_result["media_id"] == first_id
    assert first_result["success"] is False
    assert first_result["error_code"] == "fotos_media_storage_conflict"
    assert second_result["media_id"] == second_id
    assert second_result["success"] is True

    assert first_old_path.read_bytes() == first_content
    assert occupied_path.read_bytes() == b"destino-ocupado"
    assert second_new_path.read_bytes() == second_content


def test_bulk_verify_original_date_reports_missing_date(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Confirma datas existentes e relata individualmente a ausência."""

    (
        _organization_id,
        _tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    dated_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="lote-com-data.jpg",
        content=create_test_jpeg(
            width=35,
            height=17,
            original_date=datetime(
                2021,
                8,
                15,
                9,
            ),
        ),
    )
    undated_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="lote-sem-data.jpg",
        content=create_test_jpeg(
            width=36,
            height=17,
        ),
    )

    assert dated_response.status_code == 201
    assert undated_response.status_code == 201

    dated_id = dated_response.json()["id"]
    undated_id = undated_response.json()["id"]

    with test_session_factory() as session:
        dated = session.get(
            FotosMediaModel,
            dated_id,
        )
        undated = session.get(
            FotosMediaModel,
            undated_id,
        )

        assert dated is not None
        assert undated is not None

        dated.original_date_verified = False
        dated.original_date_conflict = True
        undated.original_date_verified = False
        undated.original_date_conflict = True
        session.commit()

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "verify_original_date",
            "media_ids": [
                dated_id,
                undated_id,
            ],
        },
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1
    assert result["results"][0]["success"] is True
    assert result["results"][0]["media"]["original_date_verified"] is True
    assert result["results"][0]["media"]["original_date_conflict"] is False
    assert result["results"][1]["success"] is False
    assert result["results"][1]["error_code"] == "fotos_media_original_date_missing"

    with test_session_factory() as session:
        undated = session.get(
            FotosMediaModel,
            undated_id,
        )

        assert undated is not None
        assert undated.original_date_verified is False
        assert undated.original_date_conflict is True


def test_bulk_clear_original_date_conflict_preserves_verification(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Limpa o conflito sem confirmar uma data ausente."""

    (
        _organization_id,
        _tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="limpar-conflito.jpg",
        content=create_test_jpeg(
            width=37,
            height=17,
        ),
    )

    assert create_response.status_code == 201

    media_id = create_response.json()["id"]

    with test_session_factory() as session:
        media = session.get(
            FotosMediaModel,
            media_id,
        )

        assert media is not None

        media.original_date_verified = False
        media.original_date_conflict = True
        session.commit()

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [media_id],
        },
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 0
    assert result["results"][0]["media"]["original_date_verified"] is False
    assert result["results"][0]["media"]["original_date_conflict"] is False


def test_bulk_set_album_handles_scope_and_removal(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Move entre álbuns, relata escopo inválido e remove associação."""

    (
        _organization_id,
        _tenant_id,
        environment_id,
        first_album_id,
        headers,
    ) = media_context

    second_album = create_album(
        client,
        SECOND_ALBUM,
        environment_id,
        headers,
    )

    primary_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=first_album_id,
        headers=headers,
        file_name="album-principal.jpg",
        content=create_test_jpeg(
            width=38,
            height=17,
        ),
    )

    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
        name="Tenant Externo",
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
        name="Ambiente Externo",
    )
    other_album = create_album(
        client,
        {
            **FIRST_ALBUM,
            "name": "álbum Externo",
        },
        str(other_environment["id"]),
        headers,
    )
    external_response = upload_image(
        client,
        environment_id=str(other_environment["id"]),
        album_id=str(other_album["id"]),
        headers=headers,
        file_name="album-externo.jpg",
        content=create_test_jpeg(
            width=39,
            height=17,
        ),
    )

    assert primary_response.status_code == 201
    assert external_response.status_code == 201

    primary_id = primary_response.json()["id"]
    external_id = external_response.json()["id"]

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_album",
            "media_ids": [
                primary_id,
                external_id,
            ],
            "album_id": second_album["id"],
        },
        headers=headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1
    assert result["results"][0]["media"]["album_id"] == second_album["id"]
    assert result["results"][1]["success"] is False
    assert result["results"][1]["error_code"] == "fotos_media_album_scope_mismatch"

    remove_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "set_album",
            "media_ids": [primary_id],
            "album_id": None,
        },
        headers=headers,
    )

    assert remove_response.status_code == 200
    assert remove_response.json()["results"][0]["media"]["album_id"] is None

    external_get = client.get(
        f"{MEDIA_URL}/{external_id}",
        headers=headers,
    )

    assert external_get.status_code == 200
    assert external_get.json()["album_id"] == other_album["id"]


def test_bulk_rejects_invalid_selection_contract(
    client: TestClient,
    media_context: tuple[
        str,
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita IDs repetidos e lotes acima do limite."""

    (
        _organization_id,
        _tenant_id,
        _environment_id,
        _album_id,
        headers,
    ) = media_context

    empty_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [],
        },
        headers=headers,
    )

    assert empty_response.status_code == 422

    repeated_id = str(uuid4())

    duplicate_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [
                repeated_id,
                repeated_id,
            ],
        },
        headers=headers,
    )

    assert duplicate_response.status_code == 422

    oversized_response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [str(uuid4()) for _ in range(101)],
        },
        headers=headers,
    )

    assert oversized_response.status_code == 422


def test_bulk_rejects_analyst(
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
    """Impede que analista execute curadoria administrativa em lote."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        administrator_headers,
    ) = media_context

    create_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=administrator_headers,
        file_name="lote-sem-permissao.jpg",
        content=create_test_jpeg(
            width=40,
            height=17,
        ),
    )

    assert create_response.status_code == 201

    analyst = create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email="analyst.bulk.fotos.media@deja.com",
        role="analyst",
    )
    analyst_headers = authorization_headers(
        test_settings,
        analyst,
    )

    response = client.patch(
        f"{MEDIA_URL}/bulk",
        json={
            "operation": "clear_original_date_conflict",
            "media_ids": [
                create_response.json()["id"],
            ],
        },
        headers=analyst_headers,
    )

    assert response.status_code == 403


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
        / "sem-data"
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


def test_reupload_deleted_media_restores_record(
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
    """Restaura uma mídia excluída ao reenviar a mesma fonte."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=24,
        height=18,
    )

    first_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert first_response.status_code == 201

    media_id = first_response.json()["id"]

    original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "sem-data"
        / media_id
        / "original.jpg"
    )

    assert original_path.is_file()

    delete_response = client.delete(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert original_path.is_file()

    restore_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="IMG-20240131-WA0001.jpg",
        content=content,
    )

    assert restore_response.status_code == 201

    restored = restore_response.json()

    assert restored["id"] == media_id
    assert restored["album_id"] == album_id
    assert restored["original_name"] == "IMG-20240131-WA0001.jpg"
    assert restored["deleted_at"] is None
    assert restored["original_date"] == "2024-01-31T00:00:00"
    assert restored["original_date_source"] == "filename"
    assert restored["original_date_precision"] == "date"
    assert restored["original_date_verified"] is False

    inferred_original_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / "2024"
        / "01"
        / media_id
        / "original.jpg"
    )

    assert not original_path.exists()
    assert inferred_original_path.is_file()

    get_response = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )

    assert get_response.status_code == 200

    list_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
        },
        headers=headers,
    )

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["id"] == media_id

    staging_root = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / ".staging"
    )

    assert not staging_root.exists() or not any(staging_root.iterdir())


def test_upload_media_rejects_duplicate_source(
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
    """Rejeita arquivo-fonte já cadastrado no mesmo ambiente."""

    (
        organization_id,
        tenant_id,
        environment_id,
        album_id,
        headers,
    ) = media_context

    content = create_test_jpeg(
        width=24,
        height=18,
    )

    first_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        content=content,
    )

    assert first_response.status_code == 201

    first = first_response.json()

    duplicate_response = upload_image(
        client,
        environment_id=environment_id,
        album_id=album_id,
        headers=headers,
        file_name="copia.jpg",
        content=content,
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"] == "fotos_media_duplicate"
    assert first["id"] in duplicate_response.json()["message"]

    list_response = client.get(
        MEDIA_URL,
        params={
            "environment_id": environment_id,
        },
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert list_response.json()["total"] == 1

    staging_root = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / ".staging"
    )

    assert not staging_root.exists() or not any(staging_root.iterdir())


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
        / "sem-data"
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
    before_ids = {derivative["derivative_type"]: derivative["id"] for derivative in before}

    thumbnail_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / "sem-data"
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
    after_ids = {derivative["derivative_type"]: derivative["id"] for derivative in after}

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
    before_ids = {derivative["derivative_type"]: derivative["id"] for derivative in before}

    preview_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / "sem-data"
        / media_id
        / "preview.mp4"
    )

    assert preview_path.is_file()

    preview_size = preview_path.stat().st_size

    assert preview_size > 0

    preview_path.write_bytes(b"\x00" * preview_size)

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
    after_ids = {derivative["derivative_type"]: derivative["id"] for derivative in after}

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
        derivative for derivative in before if derivative["derivative_type"] == "preview"
    )

    preview_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / "sem-data"
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

    preview_path.write_bytes(b"orphan-derivative")

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
        derivative for derivative in after if derivative["derivative_type"] == "preview"
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
    before_ids = {derivative["derivative_type"]: derivative["id"] for derivative in before}

    derivatives_path = (
        test_settings.uploads_dir
        / "fotos"
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / "sem-data"
        / media_id
    )
    thumbnail_path = derivatives_path / "thumbnail.webp"
    preview_path = derivatives_path / "preview.webp"

    assert thumbnail_path.is_file()
    assert preview_path.is_file()

    thumbnail_path.unlink()
    preview_path.unlink()

    original_generate = derivative_service_module.generate_image_derivative

    def generate_with_preview_failure(
        source_path: Path,
        destination_path: Path,
        *,
        derivative_type: str,
    ):
        if derivative_type == "preview":
            raise FotosImageDerivativeError("Falha simulada no preview.")

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
    after_ids = {derivative["derivative_type"]: derivative["id"] for derivative in after}

    assert len(after) == 2
    assert after_ids == before_ids

    media_response = client.get(
        f"{MEDIA_URL}/{media_id}",
        headers=headers,
    )

    assert media_response.status_code == 200
    assert media_response.json()["processing_status"] == "failed"
    assert media_response.json()["processing_error"] == "Falha simulada no preview."


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
        minutes=(test_settings.fotos_media_processing_timeout_minutes + 1),
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
