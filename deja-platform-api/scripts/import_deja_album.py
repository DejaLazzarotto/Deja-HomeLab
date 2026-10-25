"""Auditoria e preparação isolada de piloto Deja Album -> VIVARO.

Execute com as dependências da API instaladas e variáveis de ambiente:
  DEJA_ALBUM_DATABASE_URL=mysql+pymysql://reader:...@127.0.0.1/deja_album
  DB_*, JWT_SECRET_KEY e demais configurações da Deja Platform (.env da API)

Por padrão somente consulta os bancos e produz um JSON. Com --prepare-pilot,
copia as 7 mídias selecionadas para uma pasta isolada; NÃO grava no MySQL
nem no armazenamento gerenciado do VIVARO. A homologação precede a importação.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import Counter
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID, uuid5

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
PERIOD = re.compile(r"^([A-Za-zÀ-ÿ]+) de (\d{4})$")
SCOPE = {
    "o": "4c151dc5-be27-4ce4-8460-177264b8b8a6",
    "t": "f4724552-4529-47eb-a21d-d833d118d15f",
    "e": "84d317db-9897-4b99-b801-f2fc18b7a784",
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".mpeg", ".mpg"}
TABLES = (
    "fotos_albums",
    "fotos_media",
    "fotos_people",
    "fotos_faces",
    "fotos_person_media",
    "fotos_album_period_descriptions",
)


def period_from_label(label: str | None):
    match = PERIOD.fullmatch((label or "").strip())
    if not match:
        return None
    month = MONTHS.get(match.group(1).casefold())
    year = int(match.group(2))
    return (year, month) if month and 1 <= year <= 9999 else None


def safe_media_path(root: Path, stored: str | None) -> Path | None:
    """Resolve apenas caminhos dentro da raiz histórica; não segue links fora dela."""
    if not stored or "\x00" in stored:
        return None
    relative = Path(stored.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        return None
    candidate = (root / relative).resolve()
    return candidate if candidate.is_relative_to(root) else None


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_source(source_engine: Engine, root: Path, photo_count: int, video_count: int) -> dict:
    with source_engine.connect() as connection:
        connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        albums = (
            connection.execute(text("SELECT id, nome FROM albuns ORDER BY id")).mappings().all()
        )
        descriptions = (
            connection.execute(
                text("SELECT id, id_album, label_mes, descricao FROM descricoes_mes ORDER BY id")
            )
            .mappings()
            .all()
        )
        media = (
            connection.execute(
                text(
                    "SELECT id, nome_original, caminho, tipo_midia, data_original, "
                    "data_upload, album_id, pessoas_detectadas, visualizacoes "
                    "FROM midias ORDER BY id"
                )
            )
            .mappings()
            .all()
        )
        people = (
            connection.execute(
                text("SELECT id, nome, foto_referencia FROM pessoas_conhecidas ORDER BY id")
            )
            .mappings()
            .all()
        )
        connection.rollback()

    album_ids = {row["id"] for row in albums}
    counts = Counter()
    exceptions = []
    preview = {"image": [], "video": []}
    seen_names = Counter((row["nome"] or "").strip().casefold() for row in people)
    for row in descriptions:
        label = row["label_mes"]
        if label == "🔥 Os 10 Mais Vistos":
            counts["descriptions_ignored_top10"] += 1
            continue
        period = period_from_label(label)
        if not period or row["id_album"] not in album_ids:
            exceptions.append(
                {
                    "kind": "invalid_description",
                    "id": row["id"],
                    "label": label,
                    "album_id": row["id_album"],
                }
            )
        else:
            counts["descriptions_valid"] += 1
    counts["albums"] = len(albums)
    counts["media"] = len(media)
    counts["people_rows"] = len(people)
    counts["people_duplicate_names"] = sum(n - 1 for n in seen_names.values() if n > 1)
    counts["descriptions_total"] = len(descriptions)

    for row in media:
        media_id = row["id"]
        ext = Path(row["nome_original"] or row["caminho"] or "").suffix.lower()
        kind = "image" if ext in IMAGE_EXTS else "video" if ext in VIDEO_EXTS else "other"
        counts[f"media_{kind}"] += 1
        if row["album_id"] is not None and row["album_id"] not in album_ids:
            exceptions.append(
                {"kind": "orphan_media_album", "id": media_id, "album_id": row["album_id"]}
            )
        path = safe_media_path(root, row["caminho"])
        if path is None:
            counts["invalid_paths"] += 1
            exceptions.append({"kind": "unsafe_path", "id": media_id})
            continue
        if not path.is_file():
            counts["missing_files"] += 1
            exceptions.append(
                {"kind": "missing_file", "id": media_id, "relative_path": row["caminho"]}
            )
            continue
        counts["present_files"] += 1
        if kind == "other":
            exceptions.append({"kind": "unsupported_extension", "id": media_id, "extension": ext})
            continue
        if len(preview[kind]) >= (photo_count if kind == "image" else video_count):
            continue
        raw_people = row["pessoas_detectadas"]
        try:
            faces = json.loads(raw_people) if isinstance(raw_people, str) else (raw_people or [])
            if not isinstance(faces, list):
                raise ValueError("JSON facial não é lista")
        except (ValueError, TypeError):
            faces = []
            exceptions.append({"kind": "invalid_faces_json", "id": media_id})
        original_date = row["data_original"]
        dest_part = (
            f"{original_date.year:04d}/{original_date.month:02d}"
            if isinstance(original_date, (date, datetime))
            else "sem-data"
        )
        preview[kind].append(
            {
                "legacy_id": media_id,
                "original_name": row["nome_original"],
                "legacy_path": row["caminho"],
                "album_id": row["album_id"],
                "original_date": original_date.isoformat() if original_date else None,
                "destination_date_partition": dest_part,
                "legacy_face_count": len(faces),
                "file_size": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    return {
        "counts": dict(sorted(counts.items())),
        "exceptions": exceptions,
        "pilot_candidates": preview,
        "albums": [{"legacy_id": r["id"], "name": r["nome"]} for r in albums],
    }


def inspect_target(target: Engine) -> dict:
    with target.connect() as connection:
        relation = connection.execute(
            text("""
            SELECT COUNT(*) FROM organizations o
            JOIN tenants t ON t.organization_id=o.id
            JOIN environments e ON e.tenant_id=t.id
            WHERE o.id=:o AND t.id=:t AND e.id=:e
        """),
            SCOPE,
        ).scalar_one()
        if relation != 1:
            raise RuntimeError(
                "Escopo institucional do destino não foi encontrado ou está inconsistente"
            )
        counts = {}
        for table in TABLES:
            counts[table] = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM {table} "
                    "WHERE organization_id=:o AND tenant_id=:t AND environment_id=:e"
                ),
                SCOPE,
            ).scalar_one()
    return {"scope": dict(SCOPE), "existing_counts": counts}


def prepare_pilot(report: dict, root: Path, pilot_dir: Path) -> dict:
    """Copia o piloto para uma pasta isolada com verificação de integridade.

    Nunca move/apaga origem; nunca escreve em UPLOADS_DIR. Execução repetida
    valida novamente cada cópia e não altera arquivos já íntegros.
    """
    from deja_platform_api.core.config import get_settings

    settings = get_settings()
    managed_root = settings.uploads_dir.resolve()
    root = root.resolve(strict=True)
    pilot_dir = pilot_dir.resolve()
    if pilot_dir == root or pilot_dir.is_relative_to(root):
        raise RuntimeError("A pasta de piloto não pode estar dentro do acervo legado.")
    if pilot_dir == managed_root or pilot_dir.is_relative_to(managed_root):
        raise RuntimeError(
            "A pasta de piloto não pode estar no armazenamento gerenciado do VIVARO."
        )
    if managed_root.is_relative_to(pilot_dir):
        raise RuntimeError("A pasta de piloto não pode conter o armazenamento do VIVARO.")
    if pilot_dir == Path("/") or len(pilot_dir.parts) < 3:
        raise RuntimeError("A pasta de piloto precisa ser um caminho isolado específico.")

    from deja_platform_api.fotos.media.storage import build_original_storage_key

    manifest = {
        "mode": "staged_pilot_no_database_writes",
        "scope": dict(SCOPE),
        "source_root": str(root),
        "staging_root": str(pilot_dir),
        "media": [],
        "warnings": ["Nenhum registro foi inserido no VIVARO."],
    }
    for kind in ("image", "video"):
        for entry in report["legacy"]["pilot_candidates"][kind]:
            legacy_id = entry["legacy_id"]
            source = safe_media_path(root, entry["legacy_path"])
            if source is None or not source.is_file() or source.is_symlink():
                raise RuntimeError(f"Origem insegura ou inexistente: {legacy_id}")
            current_sha = file_sha256(source)
            if current_sha != entry["sha256"]:
                raise RuntimeError(f"SHA-256 alterado durante a auditoria: {legacy_id}")
            # IDs estáveis na preparação; aplicação futura utilizará o mesmo mapa.
            media_id = str(uuid5(UUID(SCOPE["e"]), f"deja-album:media:{legacy_id}"))
            date_text = entry["original_date"]
            # Datas não demonstradas pelos metadados dos vídeos do piloto ficam pendentes.
            effective_date = (
                None
                if kind == "video" and legacy_id in (309, 310)
                else (datetime.fromisoformat(date_text) if date_text else None)
            )
            extension = source.suffix.lower()
            key = build_original_storage_key(
                organization_id=SCOPE["o"],
                tenant_id=SCOPE["t"],
                environment_id=SCOPE["e"],
                media_id=media_id,
                file_extension=extension,
                original_date=effective_date,
            )
            # O manifesto contém o caminho de destino; a cópia permanece ISOLADA.
            destination = pilot_dir / key
            if destination.exists():
                if (
                    not destination.is_file()
                    or destination.is_symlink()
                    or file_sha256(destination) != current_sha
                ):
                    raise RuntimeError(f"Arquivo de piloto preexistente em conflito: {destination}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                temp = destination.with_name(destination.name + ".partial")
                if temp.exists():
                    raise RuntimeError(f"Cópia parcial preexistente: {temp}")
                try:
                    with source.open("rb") as source_file, temp.open("xb") as dest_file:
                        shutil.copyfileobj(source_file, dest_file, length=1024 * 1024)
                    if file_sha256(temp) != current_sha:
                        raise RuntimeError(f"Falha de integridade na cópia: {legacy_id}")
                    temp.replace(destination)
                finally:
                    temp.unlink(missing_ok=True)
            item = dict(entry)
            item.update(
                {
                    "media_uuid": media_id,
                    "managed_storage_key_proposed": key.as_posix(),
                    "staged_file": str(destination),
                    "staged_sha256": current_sha,
                    "date_for_import": effective_date.isoformat() if effective_date else None,
                    "date_requires_review": kind == "video" and legacy_id in (309, 310),
                }
            )
            manifest["media"].append(item)
    return manifest


def plan_database_pilot(source_engine, target_engine, manifest_path):
    """Plano de integração, sem SQL de escrita ou cópias físicas."""
    from PIL import Image

    manifest_path = manifest_path.resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mode") != "staged_pilot_no_database_writes" or manifest.get("scope") != SCOPE:
        raise RuntimeError("Manifesto de piloto incompatível com o destino.")
    items = manifest.get("media", [])
    if len(items) != 7 or len({m["legacy_id"] for m in items}) != 7:
        raise RuntimeError("O piloto precisa conter exatamente sete mídias distintas.")
    stage_root = Path(manifest["staging_root"]).resolve(strict=True)
    from deja_platform_api.core.config import get_settings

    managed_root = get_settings().uploads_dir.resolve()
    legacy_root = Path(manifest["source_root"]).resolve(strict=True)
    if stage_root == managed_root or stage_root.is_relative_to(managed_root):
        raise RuntimeError("Área isolada dentro do armazenamento gerenciado.")
    if stage_root == legacy_root or stage_root.is_relative_to(legacy_root):
        raise RuntimeError("Área isolada dentro do armazenamento legado.")

    ids = [int(m["legacy_id"]) for m in items]
    sql_params = {f"id{i}": value for i, value in enumerate(ids)}
    places = ", ".join(f":id{i}" for i in range(len(ids)))
    with source_engine.connect() as source:
        source.exec_driver_sql("SET TRANSACTION READ ONLY")
        medias = {
            r["id"]: dict(r)
            for r in source.execute(
                text(
                    f"SELECT id, nome_original, caminho, tipo_midia, data_original, album_id, "
                    f"pessoas_detectadas, visualizacoes FROM midias WHERE id IN ({places})"
                ),
                sql_params,
            ).mappings()
        }
        album_ids = sorted({r["album_id"] for r in medias.values() if r["album_id"] is not None})
        album_params = {f"a{i}": value for i, value in enumerate(album_ids)}
        album_places = ", ".join(f":a{i}" for i in range(len(album_ids)))
        albums = {
            r["id"]: dict(r)
            for r in source.execute(
                text(f"SELECT id, nome FROM albuns WHERE id IN ({album_places})"), album_params
            ).mappings()
        }
        descriptions = [
            dict(r)
            for r in source.execute(
                text(
                    f"SELECT id, id_album, label_mes, descricao FROM descricoes_mes "
                    f"WHERE id_album IN ({album_places}) ORDER BY id"
                ),
                album_params,
            ).mappings()
        ]
        source.rollback()
    if set(ids) != set(medias) or set(album_ids) != set(albums):
        raise RuntimeError("Mídias ou álbuns do manifesto desapareceram do legado.")

    from uuid import UUID, uuid5

    planned_albums = [
        {
            "legacy_id": a,
            "vivaro_id": str(uuid5(UUID(SCOPE["e"]), f"deja-album:album:{a}")),
            "name": albums[a]["nome"],
        }
        for a in album_ids
    ]
    planned_descriptions = []
    blocked = []
    for r in descriptions:
        if r["label_mes"] == "🔥 Os 10 Mais Vistos":
            continue
        period = period_from_label(r["label_mes"])
        if not period:
            blocked.append({"kind": "invalid_month", "description_id": r["id"]})
            continue
        planned_descriptions.append(
            {
                "legacy_id": r["id"],
                "album_legacy_id": r["id_album"],
                "year": period[0],
                "month": period[1],
                "description": r["descricao"] or "",
            }
        )
    description_keys = [(d["album_legacy_id"], d["year"], d["month"]) for d in planned_descriptions]
    if len(description_keys) != len(set(description_keys)):
        blocked.append({"kind": "duplicate_album_month_descriptions"})

    planned_media = []
    names = set()
    for entry in items:
        legacy_id = int(entry["legacy_id"])
        db = medias[legacy_id]
        if db["caminho"] != entry["legacy_path"] or db["nome_original"] != entry["original_name"]:
            blocked.append({"kind": "legacy_metadata_changed", "legacy_id": legacy_id})
        staged = Path(entry["staged_file"])
        if not staged.is_relative_to(stage_root) or staged.is_symlink() or not staged.is_file():
            blocked.append({"kind": "staged_file_missing_or_unsafe", "legacy_id": legacy_id})
            continue
        checksum = file_sha256(staged)
        if checksum != entry["sha256"] or checksum != entry["staged_sha256"]:
            blocked.append({"kind": "staged_hash_mismatch", "legacy_id": legacy_id})
            continue
        # Validação da origem também, sem leitura indiscriminada de outros arquivos.
        source_file = safe_media_path(legacy_root, entry["legacy_path"])
        if source_file is None or not source_file.is_file() or file_sha256(source_file) != checksum:
            blocked.append({"kind": "legacy_source_changed", "legacy_id": legacy_id})
            continue
        medium = (
            "image"
            if db["tipo_midia"] == "foto"
            else "video"
            if db["tipo_midia"] == "video"
            else None
        )
        if medium is None:
            blocked.append({"kind": "invalid_legacy_type", "legacy_id": legacy_id})
            continue
        faces = db["pessoas_detectadas"]
        try:
            faces = json.loads(faces) if isinstance(faces, str) else faces or []
            if not isinstance(faces, list):
                raise ValueError
        except (TypeError, ValueError):
            faces = []
            blocked.append({"kind": "bad_faces_json", "legacy_id": legacy_id})
        facial_plan = []
        if medium == "image":
            with Image.open(staged) as img:
                width, height = img.size
                orientation = int(img.getexif().get(274, 1))
            for idx, face in enumerate(faces):
                if (
                    not isinstance(face, dict)
                    or not isinstance(face.get("box"), (list, tuple))
                    or len(face["box"]) != 4
                ):
                    blocked.append(
                        {"kind": "invalid_face_box", "legacy_id": legacy_id, "index": idx}
                    )
                    continue
                top, right, bottom, left = face["box"]
                if not all(isinstance(n, (int, float)) for n in (top, right, bottom, left)):
                    blocked.append(
                        {"kind": "non_numeric_face_box", "legacy_id": legacy_id, "index": idx}
                    )
                    continue
                if (
                    not (0 <= left < right <= width and 0 <= top < bottom <= height)
                    or orientation != 1
                ):
                    blocked.append(
                        {
                            "kind": "face_box_or_orientation_requires_review",
                            "legacy_id": legacy_id,
                            "index": idx,
                            "orientation": orientation,
                        }
                    )
                    continue
                name = str(face.get("nome") or "").strip()
                if not name:
                    blocked.append(
                        {"kind": "face_without_person_name", "legacy_id": legacy_id, "index": idx}
                    )
                    continue
                names.add(name)
                facial_plan.append(
                    {
                        "name": name,
                        "x": left / width,
                        "y": top / height,
                        "width": (right - left) / width,
                        "height": (bottom - top) / height,
                        "status_proposed": "unknown_pending_review",
                    }
                )
        planned_media.append(
            {
                "legacy_id": legacy_id,
                "vivaro_id": entry["media_uuid"],
                "album_legacy_id": db["album_id"],
                "media_type": medium,
                "original_name": db["nome_original"],
                "staged_file": str(staged),
                "storage_key": entry["managed_storage_key_proposed"],
                "source_sha256": checksum,
                "source_size": staged.stat().st_size,
                "date_for_import": entry["date_for_import"],
                "legacy_date": db["data_original"].isoformat() if db["data_original"] else None,
                "faces_for_review": facial_plan,
            }
        )
    with target_engine.connect() as target:
        duplicates = []
        for entry in planned_media:
            collisions = (
                target.execute(
                    text(
                        "SELECT id FROM fotos_media WHERE environment_id=:environment AND "
                        "(id=:media OR source_checksum_sha256=:sha)"
                    ),
                    {
                        "environment": SCOPE["e"],
                        "media": entry["vivaro_id"],
                        "sha": entry["source_sha256"],
                    },
                )
                .scalars()
                .all()
            )
            if collisions:
                duplicates.append(
                    {"legacy_id": entry["legacy_id"], "existing_media_ids": collisions}
                )
    if duplicates:
        blocked.append({"kind": "existing_target_media", "collisions": duplicates})
    return {
        "mode": "database_pilot_plan_only",
        "scope": dict(SCOPE),
        "ready_for_implementation": not blocked and len(planned_media) == 7,
        "albums": planned_albums,
        "descriptions": planned_descriptions,
        "people_names_from_pilot": sorted(names),
        "media": planned_media,
        "blockers": blocked,
        "note": "NENHUM registro, derivado ou arquivo gerenciado foi criado.",
    }


def apply_database_pilot(
    plan_path: Path,
    *,
    expected_sha256: str,
    report_path: Path,
    session_factory=None,
    settings_override=None,
) -> dict:
    """Aplica apenas o piloto previamente aprovado. Retomável, sem tocar no legado."""
    from uuid import UUID, uuid5

    from deja_platform_api.core.config import get_settings
    from deja_platform_api.core.database import SessionLocal
    from deja_platform_api.fotos.albums.models import (
        FotosAlbumModel,
        FotosAlbumPeriodDescriptionModel,
    )
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.derivative_repository import FotosMediaDerivativeRepository
    from deja_platform_api.fotos.media.derivative_service import FotosMediaDerivativeService
    from deja_platform_api.fotos.media.inspection import inspect_image
    from deja_platform_api.fotos.media.models import FotosMediaModel
    from deja_platform_api.fotos.media.repository import FotosMediaRepository
    from deja_platform_api.fotos.media.video_inspection import inspect_video
    from deja_platform_api.fotos.people.models import FotosPersonModel

    plan_path = plan_path.resolve(strict=True)
    actual_hash = file_sha256(plan_path)
    if actual_hash != expected_sha256.lower():
        raise RuntimeError(
            "SHA-256 do plano não corresponde ao aprovado. Nenhuma gravação realizada."
        )
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if (
        plan.get("mode") != "database_pilot_plan_only"
        or plan.get("scope") != SCOPE
        or not plan.get("ready_for_implementation")
        or plan.get("blockers")
    ):
        raise RuntimeError("Plano não aprovado, escopo divergente ou com pendências.")
    medias = plan["media"]
    if len(medias) != 7 or {int(m["legacy_id"]) for m in medias} != {
        241,
        242,
        243,
        244,
        245,
        309,
        310,
    }:
        raise RuntimeError("Este executor só permite o piloto de sete mídias já escolhido.")
    if len(plan["albums"]) != 3:
        raise RuntimeError("Quantidade inesperada de álbuns do piloto.")
    if (session_factory is None) != (settings_override is None):
        raise RuntimeError(
            "Testes devem fornecer session_factory e settings_override juntos."
        )
    if session_factory is not None:
        if settings_override.app_env != "testing" or not settings_override.db_name.endswith(
            "_test"
        ):
            raise RuntimeError("Dependências injetadas exigem ambiente e banco de testes.")
        SessionLocal = session_factory
    settings = settings_override if settings_override is not None else get_settings()
    root = settings.uploads_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    scope = dict(organization_id=SCOPE["o"], tenant_id=SCOPE["t"], environment_id=SCOPE["e"])
    scope_folder = root / "fotos" / SCOPE["o"] / SCOPE["t"] / SCOPE["e"]
    report = {
        "mode": "pilot_apply",
        "plan_sha256": actual_hash,
        "media": [],
        "status": "in_progress",
    }

    def save_report():
        report_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = report_path.with_suffix(report_path.suffix + ".partial")
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(report_path)

    # Pré-verificação de todo o lote, sem gravações. Retomadas usam o caminho
    # gerenciado ATUAL do banco, que pode ter mudado após uma conversão.
    paths = {}
    for m in medias:
        staged = Path(m["staged_file"])
        if staged.is_symlink() or not staged.is_file() or file_sha256(staged) != m["source_sha256"]:
            raise RuntimeError(f"Cópia do piloto inválida para {m['legacy_id']}")
        staged = staged.resolve(strict=True)
        key = Path(m["storage_key"])
        if key.is_absolute() or ".." in key.parts:
            raise RuntimeError("Chave de armazenamento inválida.")
        dest = root / key
        if not dest.is_relative_to(scope_folder) or dest.is_symlink():
            raise RuntimeError("Destino de armazenamento fora do escopo.")
        paths[int(m["legacy_id"])] = (staged, dest, False, m["source_sha256"])

    album_map = {int(a["legacy_id"]): a for a in plan["albums"]}
    if len({a["name"] for a in plan["albums"]}) != len(plan["albums"]):
        raise RuntimeError("Nomes de álbuns duplicados no plano.")
    with SessionLocal() as session:
        for m in medias:
            existing = session.get(FotosMediaModel, m["vivaro_id"])
            if existing and (
                existing.source_checksum_sha256 != m["source_sha256"]
                or existing.organization_id != SCOPE["o"]
                or existing.tenant_id != SCOPE["t"]
                or existing.environment_id != SCOPE["e"]
                or existing.media_type != m["media_type"]
            ):
                raise RuntimeError(f"UUID de mídia conflitante: {m['legacy_id']}")
            legacy_id = int(m["legacy_id"])
            staged, planned_dest, _, _ = paths[legacy_id]
            if existing:
                current_key = Path(existing.original_storage_key)
                if current_key.is_absolute() or ".." in current_key.parts:
                    raise RuntimeError(f"Chave gerenciada inválida: {legacy_id}")
                current_dest = root / current_key
                if (
                    not current_dest.is_relative_to(scope_folder)
                    or current_dest.is_symlink()
                    or not current_dest.is_file()
                    or file_sha256(current_dest) != existing.checksum_sha256
                ):
                    raise RuntimeError(f"Arquivo gerenciado inconsistente: {legacy_id}")
                paths[legacy_id] = (staged, current_dest, True, existing.checksum_sha256)
            elif planned_dest.exists() and (
                not planned_dest.is_file() or file_sha256(planned_dest) != m["source_sha256"]
            ):
                raise RuntimeError(f"Conflito de arquivo: {planned_dest}")
            duplicate = (
                session.query(FotosMediaModel)
                .filter_by(environment_id=SCOPE["e"], source_checksum_sha256=m["source_sha256"])
                .first()
            )
            if duplicate and duplicate.id != m["vivaro_id"]:
                raise RuntimeError(f"Checksum já cadastrado em outra mídia: {m['legacy_id']}")
        for a in plan["albums"]:
            existing = session.get(FotosAlbumModel, a["vivaro_id"])
            if existing and (existing.name != a["name"] or existing.environment_id != SCOPE["e"]):
                raise RuntimeError(f"Álbum conflitante: {a['legacy_id']}")
            duplicate = (
                session.query(FotosAlbumModel)
                .filter_by(environment_id=SCOPE["e"], name=a["name"])
                .first()
            )
            if duplicate and duplicate.id != a["vivaro_id"]:
                raise RuntimeError(f"Já existe outro álbum com nome {a['name']}")
        for name in plan["people_names_from_pilot"]:
            uid = str(uuid5(UUID(SCOPE["e"]), "deja-album:person:" + name.casefold()))
            existing = session.get(FotosPersonModel, uid)
            if existing and (existing.name != name or existing.environment_id != SCOPE["e"]):
                raise RuntimeError(f"Pessoa conflitante: {name}")
            duplicate = (
                session.query(FotosPersonModel)
                .filter_by(environment_id=SCOPE["e"], name=name)
                .first()
            )
            if duplicate and duplicate.id != uid:
                raise RuntimeError(f"Nome já cadastrado em outra pessoa: {name}")

    # Cadastros independentes e determinísticos. Nenhuma exclusão no destino.
    with SessionLocal() as session:
        with session.begin():
            for a in plan["albums"]:
                if session.get(FotosAlbumModel, a["vivaro_id"]) is None:
                    session.add(
                        FotosAlbumModel(id=a["vivaro_id"], **scope, name=a["name"], active=True)
                    )
            for d in plan["descriptions"]:
                album_uid = album_map[int(d["album_legacy_id"])]["vivaro_id"]
                uid = str(uuid5(UUID(SCOPE["e"]), f"deja-album:description:{d['legacy_id']}"))
                if session.get(FotosAlbumPeriodDescriptionModel, uid) is None:
                    session.add(
                        FotosAlbumPeriodDescriptionModel(
                            id=uid,
                            **scope,
                            album_id=album_uid,
                            original_year=int(d["year"]),
                            original_month=int(d["month"]),
                            description=d["description"],
                        )
                    )
            for name in plan["people_names_from_pilot"]:
                uid = str(uuid5(UUID(SCOPE["e"]), "deja-album:person:" + name.casefold()))
                if session.get(FotosPersonModel, uid) is None:
                    session.add(FotosPersonModel(id=uid, **scope, name=name, active=True))
    save_report()

    for m in medias:
        legacy_id = int(m["legacy_id"])
        staged, dest, already_imported, expected_managed_sha = paths[legacy_id]
        result = {"legacy_id": legacy_id, "vivaro_id": m["vivaro_id"], "status": "started"}
        report["media"].append(result)
        save_report()
        try:
            # Nunca substitui um arquivo existente; copia e verifica antes do commit.
            if not already_imported and not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                temp = dest.with_suffix(dest.suffix + ".partial")
                if temp.exists():
                    raise RuntimeError(f"Cópia parcial preexistente: {temp}")
                try:
                    with staged.open("rb") as fsrc, temp.open("xb") as fdst:
                        shutil.copyfileobj(fsrc, fdst, length=1024 * 1024)
                    if file_sha256(temp) != m["source_sha256"]:
                        raise RuntimeError("SHA-256 divergiu durante a cópia")
                    temp.replace(dest)
                finally:
                    temp.unlink(missing_ok=True)
            if not dest.is_file() or file_sha256(dest) != expected_managed_sha:
                raise RuntimeError("Arquivo gerenciado com checksum inválido")
            media_type = m["media_type"]
            if media_type == "image":
                inspection = inspect_image(dest)
                width, height, duration = inspection.width, inspection.height, None
                mime = "image/jpeg"  # O piloto tem cinco JPGs.
                if inspection.format != "JPEG":
                    raise RuntimeError("O piloto esperava JPEG")
            else:
                inspection = inspect_video(dest, ffprobe_executable=settings.ffprobe_executable)
                width, height, duration = (
                    inspection.width,
                    inspection.height,
                    inspection.duration_seconds,
                )
                mime = "video/mp4"
            dt = datetime.fromisoformat(m["date_for_import"]) if m["date_for_import"] else None
            with SessionLocal() as session:
                with session.begin():
                    record = session.get(FotosMediaModel, m["vivaro_id"])
                    if record is None:
                        album = (
                            album_map[int(m["album_legacy_id"])]["vivaro_id"]
                            if m["album_legacy_id"] is not None
                            else None
                        )
                        session.add(
                            FotosMediaModel(
                                id=m["vivaro_id"],
                                **scope,
                                album_id=album,
                                original_name=m["original_name"],
                                source_content_type=mime,
                                source_file_extension=dest.suffix,
                                source_file_size=m["source_size"],
                                source_checksum_sha256=m["source_sha256"],
                                media_type=media_type,
                                content_type=mime,
                                file_extension=dest.suffix,
                                file_size=m["source_size"],
                                checksum_sha256=m["source_sha256"],
                                is_animated=False,
                                was_converted=False,
                                original_storage_key=m["storage_key"],
                                processing_status="received",
                                original_date=dt,
                                original_date_source="manual" if dt else None,
                                original_date_precision="datetime" if dt else None,
                                original_date_verified=False,
                                original_date_conflict=False,
                                width=width,
                                height=height,
                                duration_seconds=duration,
                                view_count=0,
                            )
                        )
            # A API confirma estado ready somente depois de processar derivados.
            with SessionLocal() as session:
                record = session.get(FotosMediaModel, m["vivaro_id"])
                service = FotosMediaDerivativeService(
                    FotosMediaRepository(session),
                    FotosMediaDerivativeRepository(session),
                    settings,
                )
                service.process(record)
            # As faces legadas são pendentes de validação. Não confirmar vínculo automaticamente.
            if media_type == "image":
                with SessionLocal() as session:
                    with session.begin():
                        for index, face in enumerate(m["faces_for_review"]):
                            fid = str(
                                uuid5(UUID(SCOPE["e"]), f"deja-album:face:{legacy_id}:{index}")
                            )
                            if session.get(FotosFaceModel, fid) is None:
                                session.add(
                                    FotosFaceModel(
                                        id=fid,
                                        **scope,
                                        media_id=m["vivaro_id"],
                                        x=face["x"],
                                        y=face["y"],
                                        width=face["width"],
                                        height=face["height"],
                                        origin="manual",
                                        status="unknown",
                                        person_id=None,
                                        confidence=None,
                                    )
                                )
            result["status"] = "ready_faces_pending_review" if media_type == "image" else "ready"
        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)
            report["status"] = "partial_failure"
            save_report()
            raise
        save_report()
    report["status"] = "completed"
    save_report()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auditoria SOMENTE LEITURA da migração Deja Album → VIVARO"
    )
    parser.add_argument("--legacy-root", type=Path, default=Path("/var/www/deja/storage/midias"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--prepare-pilot",
        action="store_true",
        help="copia o piloto para pasta isolada, sem gravar no banco",
    )
    parser.add_argument(
        "--pilot-dir",
        type=Path,
        help="pasta isolada para as cópias; obrigatória com --prepare-pilot",
    )
    parser.add_argument(
        "--plan-db-pilot",
        type=Path,
        help="manifesto validado; gera plano de integração SEM GRAVAR no banco",
    )
    parser.add_argument(
        "--apply-db-plan", type=Path, help="aplica EXCLUSIVAMENTE o piloto com SHA aprovado"
    )
    parser.add_argument("--approved-sha256", help="SHA-256 exigido para aplicar o plano")
    parser.add_argument("--photos", type=int, default=5)
    parser.add_argument("--videos", type=int, default=2)
    args = parser.parse_args()
    if args.apply_db_plan is not None and (
        not args.approved_sha256 or args.prepare_pilot or args.plan_db_pilot or args.pilot_dir
    ):
        parser.error("--apply-db-plan exige --approved-sha256 e não aceita outros modos")
    if args.approved_sha256 and not args.apply_db_plan:
        parser.error("--approved-sha256 requer --apply-db-plan")
    if args.plan_db_pilot is not None and (args.prepare_pilot or args.pilot_dir is not None):
        parser.error("--plan-db-pilot não pode ser combinado com a preparação de cópias")
    if args.prepare_pilot and args.pilot_dir is None:
        parser.error("--prepare-pilot exige --pilot-dir")
    if args.pilot_dir is not None and not args.prepare_pilot:
        parser.error("--pilot-dir exige --prepare-pilot")
    if args.photos < 0 or args.videos < 0:
        parser.error("--photos e --videos não podem ser negativos")
    if args.apply_db_plan is not None:
        result = apply_database_pilot(
            args.apply_db_plan, expected_sha256=args.approved_sha256, report_path=args.output
        )
        print("PILOTO APLICADO:", result["status"], "Mídias:", len(result["media"]))
        return
    source_url = os.getenv("DEJA_ALBUM_DATABASE_URL")
    if not source_url:
        parser.error("Configure DEJA_ALBUM_DATABASE_URL com credenciais de LEITURA do banco legado")
    if urlsplit(source_url).scheme not in {"mysql+pymysql", "mysql"}:
        parser.error("A origem deve usar uma conexão MySQL")
    root = args.legacy_root.resolve(strict=True)
    if not root.is_dir():
        parser.error("--legacy-root precisa apontar para diretório existente")
    from deja_platform_api.core.database import engine as target_engine

    source_engine = create_engine(source_url, pool_pre_ping=True)
    if args.plan_db_pilot is not None:
        try:
            plan = plan_database_pilot(source_engine, target_engine, args.plan_db_pilot)
        finally:
            source_engine.dispose()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        print("PLANO DE INTEGRAÇÃO GERADO — nenhum banco ou arquivo gerenciado foi modificado.")
        print(
            "Álbuns:",
            len(plan["albums"]),
            "Descrições:",
            len(plan["descriptions"]),
            "Pessoas:",
            len(plan["people_names_from_pilot"]),
            "Mídias:",
            len(plan["media"]),
        )
        print("Pendências:", len(plan["blockers"]))
        print("Relatório:", args.output)
        return
    try:
        report = {
            "mode": "dry_run_read_only",
            "timestamp": datetime.now().isoformat(),
            "source_root": str(root),
            "target": inspect_target(target_engine),
            "legacy": inspect_source(source_engine, root, args.photos, args.videos),
        }
    finally:
        source_engine.dispose()
    if args.prepare_pilot:
        manifest = prepare_pilot(report, root, args.pilot_dir)
        manifest_path = args.output.with_name(args.output.stem + "-pilot-manifest.json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("PILOTO PREPARADO — arquivos copiados fora do VIVARO:", len(manifest["media"]))
        print("Manifesto:", manifest_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("AUDITORIA CONCLUÍDA — nenhum banco de dados ou arquivo legado foi alterado.")
    print("Relatório:", args.output)
    print("Contagens:", json.dumps(report["legacy"]["counts"], ensure_ascii=False))
    print("Exceções:", len(report["legacy"]["exceptions"]))
    print(
        "Piloto:",
        len(report["legacy"]["pilot_candidates"]["image"]),
        "fotos +",
        len(report["legacy"]["pilot_candidates"]["video"]),
        "vídeos",
    )


if __name__ == "__main__":
    main()
