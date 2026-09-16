from datetime import datetime
from pathlib import Path


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

    date_path = (
        Path(
            f"{original_date.year:04d}",
            f"{original_date.month:02d}",
        )
        if original_date is not None
        else Path("sem-data")
    )

    return (
        Path("fotos")
        / organization_id
        / tenant_id
        / environment_id
        / "originals"
        / date_path
        / media_id
        / f"original{file_extension}"
    )