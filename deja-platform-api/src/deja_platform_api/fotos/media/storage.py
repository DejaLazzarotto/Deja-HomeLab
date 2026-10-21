from datetime import datetime
from pathlib import Path


def build_media_date_path(
    original_date: datetime | None,
) -> Path:
    """Monta a partição de armazenamento por ano e mês."""

    if original_date is None:
        return Path("sem-data")

    return Path(
        f"{original_date.year:04d}",
        f"{original_date.month:02d}",
    )


def build_original_storage_key(
    *,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
    media_id: str,
    file_extension: str,
    original_date: datetime | None,
) -> Path:
    """Monta o caminho gerenciado do original por ano e mês."""

    return (
        Path("fotos")
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / build_media_date_path(original_date)
        / media_id
        / f"original{file_extension}"
    )


def build_derivative_storage_key(
    *,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
    media_id: str,
    derivative_type: str,
    file_extension: str,
    original_date: datetime | None,
) -> Path:
    """Monta o caminho de um derivado por ano e mês."""

    return (
        Path("fotos")
        / organization_id
        / tenant_id
        / environment_id
        / "derivatives"
        / build_media_date_path(original_date)
        / media_id
        / f"{derivative_type}{file_extension}"
    )
