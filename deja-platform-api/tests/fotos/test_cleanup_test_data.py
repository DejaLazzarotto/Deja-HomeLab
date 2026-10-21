"""Integracao da limpeza com arquivos reais e banco isolado."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "cleanup_fotos_test_data.py"
spec = importlib.util.spec_from_file_location("cleanup_fotos_test_data", SCRIPT)
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


@pytest.mark.parametrize("include_albums", [False, True])
def test_preview_and_execute_preserve_other_scopes(tmp_path, monkeypatch, capsys, include_albums):
    db = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    scope_columns = "organization_id TEXT, tenant_id TEXT, environment_id TEXT"
    tables = {
        "fotos_media": f"id TEXT, {scope_columns}, original_storage_key TEXT",
        "fotos_media_derivatives": "id TEXT, media_id TEXT, storage_key TEXT",
        "fotos_faces": f"id TEXT, {scope_columns}",
        "fotos_face_references": f"id TEXT, {scope_columns}, storage_key TEXT",
        "fotos_person_media": f"person_id TEXT, media_id TEXT, {scope_columns}",
        "fotos_people": f"id TEXT, {scope_columns}, avatar_storage_key TEXT",
        "fotos_albums": f"id TEXT, {scope_columns}",
        "fotos_album_period_descriptions": (
            f"id TEXT, album_id TEXT, {scope_columns}, description TEXT"
        ),
    }
    root = tmp_path / "uploads"
    root.mkdir()
    with db.begin() as c:
        for table, columns in tables.items():
            c.execute(text(f"CREATE TABLE {table} ({columns})"))
        for env in ("target", "other"):
            key = f"fotos/org/tenant/{env}/originals/one.jpg"
            path = root / key
            path.parent.mkdir(parents=True)
            path.write_bytes(b"image")
            c.execute(
                text("INSERT INTO fotos_media VALUES (:id,'org','tenant',:env,:key)"),
                {"id": env, "env": env, "key": key},
            )
            c.execute(
                text("INSERT INTO fotos_albums VALUES (:id,'org','tenant',:env)"),
                {"id": env, "env": env},
            )
        c.execute(
            text(
                "INSERT INTO fotos_album_period_descriptions VALUES "
                "('period','target','org','tenant','target','preserve')"
            )
        )
    monkeypatch.setattr(cleanup, "engine", db)
    monkeypatch.setattr(cleanup, "get_settings", lambda: SimpleNamespace(uploads_dir=root))
    args = ["cleanup", "--organization", "org", "--tenant", "tenant", "--environment", "target"]
    if include_albums:
        args.append("--include-albums")
    monkeypatch.setattr(sys, "argv", args)
    cleanup.main()
    fingerprint = capsys.readouterr().out.split("Fingerprint: ")[1].splitlines()[0]
    with db.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM fotos_media")).scalar_one() == 2
    monkeypatch.setattr(sys, "argv", args + ["--execute", "--fingerprint", fingerprint])
    cleanup.main()
    with db.connect() as c:
        assert c.execute(text("SELECT id FROM fotos_media")).scalars().all() == ["other"]
        assert c.execute(text("SELECT COUNT(*) FROM fotos_albums")).scalar_one() == (
            1 if include_albums else 2
        )
        assert c.execute(
            text("SELECT COUNT(*) FROM fotos_album_period_descriptions")
        ).scalar_one() == (0 if include_albums else 1)
    assert not (root / "fotos/org/tenant/target/originals/one.jpg").exists()
    assert (root / "fotos/org/tenant/other/originals/one.jpg").exists()


def test_rejects_orphan_file_before_database_change(tmp_path):
    root = tmp_path / "uploads"
    folder = root / "fotos/org/tenant/target"
    folder.mkdir(parents=True)
    (folder / "orphan.jpg").write_bytes(b"unexpected")
    try:
        cleanup.validate_files(root, {"o": "org", "t": "tenant", "e": "target"}, [])
    except RuntimeError as exc:
        assert "sem registro" in str(exc)
    else:
        raise AssertionError("Arquivo orfao deveria impedir a limpeza")
