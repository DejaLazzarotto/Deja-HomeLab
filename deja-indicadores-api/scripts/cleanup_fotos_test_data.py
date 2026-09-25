"""Remove um acervo de teste de um ambiente do Deja Fotos.

Use primeiro a previa. Para executar, pare a API e informe o fingerprint da
previa. --include-albums tambem remove albuns e descricoes mensais do escopo.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from deja_indicadores_api.core.config import get_settings
from deja_indicadores_api.core.database import engine

TABLES = (
    "fotos_media",
    "fotos_media_derivatives",
    "fotos_faces",
    "fotos_face_references",
    "fotos_person_media",
    "fotos_people",
    "fotos_album_period_descriptions",
    "fotos_albums",
)
CHILDREN = (
    "fotos_face_references",
    "fotos_faces",
    "fotos_person_media",
    "fotos_media_derivatives",
    "fotos_media",
    "fotos_people",
    "fotos_album_period_descriptions",
    "fotos_albums",
)
SCOPE_SQL = "organization_id=:o AND tenant_id=:t AND environment_id=:e"
MEDIA_SCOPE_SQL = "m.organization_id=:o AND m.tenant_id=:t AND m.environment_id=:e"
FILE_QUERIES = (
    f"SELECT original_storage_key FROM fotos_media WHERE {SCOPE_SQL}",
    "SELECT d.storage_key FROM fotos_media_derivatives d "
    f"JOIN fotos_media m ON m.id=d.media_id WHERE {MEDIA_SCOPE_SQL}",
    f"SELECT storage_key FROM fotos_face_references WHERE {SCOPE_SQL}",
    f"SELECT avatar_storage_key FROM fotos_people WHERE {SCOPE_SQL} "
    "AND avatar_storage_key IS NOT NULL",
)


def snapshot(connection, scope, include_albums):
    counts = {}
    for table in TABLES:
        if table == "fotos_media_derivatives":
            query = (
                "SELECT COUNT(*) FROM fotos_media_derivatives d "
                f"JOIN fotos_media m ON m.id=d.media_id WHERE {MEDIA_SCOPE_SQL}"
            )
        else:
            query = f"SELECT COUNT(*) FROM {table} WHERE {SCOPE_SQL}"
        counts[table] = connection.execute(
            text(query),
            scope,
        ).scalar_one()
    ids = {}
    for table in TABLES:
        if table == "fotos_media_derivatives":
            query = (
                "SELECT d.id FROM fotos_media_derivatives d "
                f"JOIN fotos_media m ON m.id=d.media_id WHERE {MEDIA_SCOPE_SQL}"
            )
        elif table == "fotos_person_media":
            query = f"SELECT person_id, media_id FROM {table} WHERE {SCOPE_SQL}"
        else:
            query = f"SELECT id FROM {table} WHERE {SCOPE_SQL}"
        ids[table] = sorted(tuple(row) for row in connection.execute(text(query), scope))
    keys = sorted(
        key for query in FILE_QUERIES for key in connection.execute(text(query), scope).scalars()
    )
    plan = {
        "scope": scope,
        "include_albums": include_albums,
        "counts": counts,
        "ids": ids,
        "keys": keys,
    }
    digest = hashlib.sha256(json.dumps(plan, sort_keys=True).encode("utf-8")).hexdigest()
    return plan, digest


def validate_files(root, scope, keys):
    root = root.resolve(strict=True)
    folder = root / "fotos" / scope["o"] / scope["t"] / scope["e"]
    if not folder.is_dir() or folder.is_symlink():
        raise RuntimeError(f"Pasta do ambiente ausente ou invalida: {folder}")
    folder = folder.resolve(strict=True)
    expected = set()
    for key in keys:
        relative = Path(key)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"Chave de armazenamento invalida: {key}")
        path = root / relative
        if not path.is_relative_to(folder) or path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Arquivo ausente, externo ou simbolico: {path}")
        if path.resolve(strict=True) != path:
            raise RuntimeError(f"Caminho com link simbolico: {path}")
        expected.add(path)
    if len(expected) != len(keys):
        raise RuntimeError("Chaves de arquivos repetidas no inventario.")
    actual = {p for p in folder.rglob("*") if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise RuntimeError(
            f"Arquivos ausentes: {sorted(str(p) for p in expected - actual)}; "
            f"arquivos sem registro: {sorted(str(p) for p in actual - expected)}"
        )
    return root, folder, expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization", required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--include-albums", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--fingerprint")
    args = parser.parse_args()
    scope = {"o": args.organization, "t": args.tenant, "e": args.environment}
    if args.execute and not args.fingerprint:
        parser.error("--execute exige --fingerprint da previa.")
    if args.fingerprint and not args.execute:
        parser.error("--fingerprint so pode acompanhar --execute.")

    with engine.connect() as connection:
        plan, digest = snapshot(connection, scope, args.include_albums)
    root, folder, paths = validate_files(get_settings().uploads_dir, scope, plan["keys"])
    print("Escopo:", scope)
    print("Registros:", plan["counts"])
    print("Arquivos:", len(paths))
    print("Pasta:", folder)
    print("Albuns e descricoes mensais:", "excluir" if args.include_albums else "preservar")
    print("Fingerprint:", digest)
    if not args.execute:
        print("PREVIA SOMENTE LEITURA. Nenhum dado foi excluido.")
        return
    if digest != args.fingerprint:
        raise RuntimeError("Inventario mudou desde a previa. Execute a previa novamente.")

    stage = root / (".fotos-cleanup-" + uuid4().hex)
    moved = []
    committed = False
    try:
        stage.mkdir()
        with engine.begin() as connection:
            updated, check = snapshot(connection, scope, args.include_albums)
            if check != digest:
                raise RuntimeError("Inventario mudou durante a execucao.")
            validate_files(root, scope, updated["keys"])
            for path in sorted(paths):
                target = stage / path.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                path.rename(target)
                moved.append((path, target))
            for table in CHILDREN:
                if (
                    table in ("fotos_albums", "fotos_album_period_descriptions")
                    and not args.include_albums
                ):
                    continue
                if table == "fotos_media_derivatives":
                    query = (
                        "DELETE FROM fotos_media_derivatives WHERE media_id IN "
                        f"(SELECT id FROM fotos_media WHERE {SCOPE_SQL})"
                    )
                else:
                    query = f"DELETE FROM {table} WHERE {SCOPE_SQL}"
                result = connection.execute(text(query), scope)
                if result.rowcount != plan["counts"][table]:
                    raise RuntimeError(f"Contagem inesperada em {table}: {result.rowcount}")
            remaining, _ = snapshot(connection, scope, args.include_albums)
            checked = CHILDREN if args.include_albums else CHILDREN[:-2]
            if any(remaining["counts"][table] for table in checked):
                raise RuntimeError("Persistem registros no escopo. Transacao cancelada.")
        committed = True
    finally:
        if not committed:
            for path, target in reversed(moved):
                path.parent.mkdir(parents=True, exist_ok=True)
                target.rename(path)
            if stage.exists():
                shutil.rmtree(stage)

    try:
        shutil.rmtree(stage)
    except OSError as exc:
        raise RuntimeError(f"Banco limpo, mas os arquivos ainda estao em {stage}") from exc
    with engine.connect() as connection:
        remaining, _ = snapshot(connection, scope, args.include_albums)
    checked = CHILDREN if args.include_albums else CHILDREN[:-2]
    if any(remaining["counts"][table] for table in checked) or any(
        p.is_file() for p in folder.rglob("*")
    ):
        raise RuntimeError("Verificacao final falhou.")
    print("Limpeza concluida e verificada.")


if __name__ == "__main__":
    main()
