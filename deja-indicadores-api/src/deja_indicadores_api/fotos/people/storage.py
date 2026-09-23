"""Caminhos de avatar dentro do armazenamento do Deja Fotos."""

from pathlib import Path


def build_avatar_storage_key(
    *,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
    person_id: str,
    avatar_id: str,
) -> Path:
    """Cria uma chave própria para uma versão do avatar."""

    return (
        Path("fotos")
        / organization_id
        / tenant_id
        / environment_id
        / "people"
        / person_id
        / "avatars"
        / f"{avatar_id}.webp"
    )


def resolve_avatar_file(
    uploads_dir: Path,
    storage_key: str,
) -> Path:
    """Impede que uma chave aponte para fora do armazenamento."""

    root = uploads_dir.resolve()
    path = (root / storage_key).resolve()

    if not path.is_relative_to(root):
        raise ValueError("Caminho de avatar inválido.")

    return path