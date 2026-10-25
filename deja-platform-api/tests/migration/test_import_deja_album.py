import subprocess
import sys
from pathlib import Path

import pytest

from deja_platform_api.fotos.media.derivative_service import (
    FotosMediaDerivativeService as _RealDerivativeService,
)

_REAL_PROCESS = _RealDerivativeService.process

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "import_deja_album.py"


def run_importer(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_apply_requires_approved_sha256(tmp_path):
    result = run_importer(
        "--apply-db-plan",
        tmp_path / "plano.json",
        "--output",
        tmp_path / "relatorio.json",
    )
    assert result.returncode != 0
    assert "--apply-db-plan exige --approved-sha256" in result.stderr
    assert not (tmp_path / "relatorio.json").exists()


def test_apply_rejects_missing_plan(tmp_path):
    result = run_importer(
        "--apply-db-plan",
        tmp_path / "inexistente.json",
        "--approved-sha256",
        "0" * 64,
        "--output",
        tmp_path / "relatorio.json",
    )
    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr
    assert not (tmp_path / "relatorio.json").exists()


def test_apply_rejects_invalid_checksum(tmp_path):
    plan = tmp_path / "plano.json"
    plan.write_text("{}", encoding="utf-8")
    result = run_importer(
        "--apply-db-plan",
        plan,
        "--approved-sha256",
        "0" * 64,
        "--output",
        tmp_path / "relatorio.json",
    )
    assert result.returncode != 0
    assert "SHA-256 do plano não corresponde" in result.stderr
    assert not (tmp_path / "relatorio.json").exists()
    assert plan.read_text(encoding="utf-8") == "{}"


def test_apply_rejects_incomplete_test_dependencies(tmp_path):
    import importlib.util
    from hashlib import sha256

    import pytest

    script = SCRIPT
    spec = importlib.util.spec_from_file_location("vivaro_importer_test", script)
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)

    plan = {
        "mode": "database_pilot_plan_only",
        "scope": importer.SCOPE,
        "ready_for_implementation": True,
        "blockers": [],
        "media": [{"legacy_id": i} for i in (241, 242, 243, 244, 245, 309, 310)],
        "albums": [{}, {}, {}],
    }

    import json

    path = tmp_path / "plano.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    checksum = sha256(path.read_bytes()).hexdigest()

    with pytest.raises(RuntimeError, match="session_factory e settings_override juntos"):
        importer.apply_database_pilot(
            path,
            expected_sha256=checksum,
            report_path=tmp_path / "relatorio.json",
            session_factory=lambda: None,
        )


def test_importer_uses_isolated_test_database(test_session_factory, test_settings):
    from sqlalchemy import text

    assert test_settings.app_env == "testing"
    assert test_settings.db_name.endswith("_test")

    with test_session_factory() as session:
        database_name = session.execute(text("SELECT DATABASE()")).scalar_one()

    assert database_name == test_settings.db_name


def test_importer_test_scope_can_create_institutional_hierarchy(
    test_session_factory,
):
    from uuid import uuid4

    from deja_platform_api.tenant_management.models import (
        EnvironmentModel,
        OrganizationModel,
        TenantModel,
    )

    organization_id = str(uuid4())
    tenant_id = str(uuid4())
    environment_id = str(uuid4())

    with test_session_factory() as session:
        with session.begin():
            session.add(
                OrganizationModel(
                    id=organization_id,
                    code=f"TEST-{organization_id[:8].upper()}",
                    name="Organização Fictícia Migração",
                )
            )
            session.flush()
            session.add(
                TenantModel(
                    id=tenant_id,
                    organization_id=organization_id,
                    name="Tenant de Testes",
                )
            )
            session.flush()
            session.add(
                EnvironmentModel(
                    id=environment_id,
                    tenant_id=tenant_id,
                    name="Ambiente de Testes",
                )
            )

        organization = session.get(OrganizationModel, organization_id)
        tenant = session.get(TenantModel, tenant_id)
        environment = session.get(EnvironmentModel, environment_id)

        assert organization is not None
        assert tenant.organization_id == organization.id
        assert environment.tenant_id == tenant.id


@pytest.fixture()
def isolated_importer_scope(test_session_factory, test_settings):
    import importlib.util
    from uuid import uuid4

    from deja_platform_api.tenant_management.models import (
        EnvironmentModel,
        OrganizationModel,
        TenantModel,
    )

    assert test_settings.app_env == "testing"
    assert test_settings.db_name.endswith("_test")

    spec = importlib.util.spec_from_file_location("vivaro_importer_isolated", SCRIPT)
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)

    scope = {
        "o": str(uuid4()),
        "t": str(uuid4()),
        "e": str(uuid4()),
    }

    assert scope != importer.SCOPE
    importer.SCOPE = scope

    with test_session_factory() as session:
        with session.begin():
            session.add(
                OrganizationModel(
                    id=scope["o"],
                    code=f"MIG-{scope['o'][:8].upper()}",
                    name="Organização de Teste do Importador",
                )
            )
            session.flush()

            session.add(
                TenantModel(
                    id=scope["t"],
                    organization_id=scope["o"],
                    name="Tenant de Migração",
                )
            )
            session.flush()

            session.add(
                EnvironmentModel(
                    id=scope["e"],
                    tenant_id=scope["t"],
                    name="Ambiente de Migração",
                )
            )

    return importer, scope


def test_isolated_importer_scope_uses_fictitious_ids(
    isolated_importer_scope,
    test_session_factory,
):
    from deja_platform_api.tenant_management.models import (
        EnvironmentModel,
        OrganizationModel,
        TenantModel,
    )

    importer, scope = isolated_importer_scope

    assert importer.SCOPE == scope
    assert scope["o"] != "4c151dc5-be27-4ce4-8460-177264b8b8a6"
    assert scope["t"] != "f4724552-4529-47eb-a21d-d833d118d15f"
    assert scope["e"] != "84d317db-9897-4b99-b801-f2fc18b7a784"

    with test_session_factory() as session:
        organization = session.get(OrganizationModel, scope["o"])
        tenant = session.get(TenantModel, scope["t"])
        environment = session.get(EnvironmentModel, scope["e"])

        assert organization is not None
        assert tenant is not None
        assert environment is not None
        assert tenant.organization_id == organization.id
        assert environment.tenant_id == tenant.id


def create_migration_test_images(tmp_path):
    from hashlib import sha256
    from io import BytesIO

    from PIL import Image

    images = []
    for index, legacy_id in enumerate((241, 242, 243, 244, 245)):
        image = Image.new("RGB", (80, 60), color=(index * 40, 80, 120))
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        content = buffer.getvalue()

        path = tmp_path / f"photo-{legacy_id}.jpg"
        path.write_bytes(content)

        images.append(
            {
                "legacy_id": legacy_id,
                "path": path,
                "sha256": sha256(content).hexdigest(),
                "size": len(content),
            }
        )

    return images


@pytest.fixture()
def migration_pilot_plan(tmp_path, isolated_importer_scope, test_settings, monkeypatch):
    """Plano integralmente fictício, sem acervo ou identificadores de produção."""
    import json
    from hashlib import sha256
    from types import SimpleNamespace
    from uuid import UUID, uuid5

    import deja_platform_api.fotos.media.video_inspection as video_inspection
    from deja_platform_api.fotos.media.derivative_service import FotosMediaDerivativeService

    importer, scope = isolated_importer_scope
    stage = tmp_path / "staging"
    stage.mkdir()
    uploads_root = test_settings.uploads_dir.resolve()
    assert stage.resolve() != uploads_root
    assert not stage.resolve().is_relative_to(uploads_root)

    assets = create_migration_test_images(stage)
    for legacy_id in (309, 310):
        content = f"SIMULATED-VIDEO-{legacy_id}".encode("ascii")
        path = stage / f"video-{legacy_id}.mp4"
        path.write_bytes(content)
        assets.append(
            {
                "legacy_id": legacy_id,
                "path": path,
                "sha256": sha256(content).hexdigest(),
                "size": len(content),
            }
        )

    monkeypatch.setattr(
        video_inspection,
        "inspect_video",
        lambda *args, **kwargs: SimpleNamespace(width=640, height=480, duration_seconds=2.0),
    )

    process_calls = []
    failure_on = {"id": None}

    def simulated_derivatives(self, media):
        process_calls.append(media.id)
        if media.id == failure_on["id"]:
            raise RuntimeError("Falha simulada na geração de derivados")
        # Processamento real de imagens e vídeos é verificado nos testes do serviço.
        # Aqui o objetivo é testar orquestração, SQL, hashes e retomada.

    monkeypatch.setattr(FotosMediaDerivativeService, "process", simulated_derivatives)

    album_ids = (3, 23, 37)
    albums = [
        {
            "legacy_id": old,
            "vivaro_id": str(uuid5(UUID(scope["e"]), f"deja-album:album:{old}")),
            "name": f"Álbum fictício {old}",
        }
        for old in album_ids
    ]
    media = []
    for asset in assets:
        legacy_id = asset["legacy_id"]
        is_photo = legacy_id < 300
        media_uid = str(uuid5(UUID(scope["e"]), f"deja-album:media:{legacy_id}"))
        date = "2008-04-05T12:00:00" if is_photo else None
        partition = "2008/04" if is_photo else "sem-data"
        key = (
            f"fotos/{scope['o']}/{scope['t']}/{scope['e']}/"
            f"{partition}/{media_uid}{asset['path'].suffix}"
        )
        media.append(
            {
                "legacy_id": legacy_id,
                "vivaro_id": media_uid,
                "album_legacy_id": album_ids[(legacy_id - 241) % len(album_ids)],
                "media_type": "image" if is_photo else "video",
                "original_name": asset["path"].name,
                "staged_file": str(asset["path"]),
                "storage_key": key,
                "source_sha256": asset["sha256"],
                "source_size": asset["size"],
                "date_for_import": date,
                "legacy_date": date,
                "faces_for_review": (
                    [
                        {
                            "name": "Pessoa Teste",
                            "x": 0.1,
                            "y": 0.1,
                            "width": 0.3,
                            "height": 0.3,
                            "status_proposed": "unknown_pending_review",
                        }
                    ]
                    if legacy_id == 241
                    else []
                ),
            }
        )
    plan = {
        "mode": "database_pilot_plan_only",
        "scope": scope,
        "ready_for_implementation": True,
        "blockers": [],
        "albums": albums,
        "descriptions": [
            {
                "legacy_id": 501,
                "album_legacy_id": 3,
                "year": 2008,
                "month": 4,
                "description": "Descrição fictícia de abril",
            },
        ],
        "people_names_from_pilot": ["Pessoa Teste"],
        "media": media,
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    approved_hash = sha256(plan_path.read_bytes()).hexdigest()
    return SimpleNamespace(
        importer=importer,
        scope=scope,
        plan=plan,
        path=plan_path,
        approved_hash=approved_hash,
        report=tmp_path / "report.json",
        process_calls=process_calls,
        failure_on=failure_on,
    )


def _apply_test_pilot(pilot, test_session_factory, test_settings):
    return pilot.importer.apply_database_pilot(
        pilot.path,
        expected_sha256=pilot.approved_hash,
        report_path=pilot.report,
        session_factory=test_session_factory,
        settings_override=test_settings,
    )


def _pilot_db_counts(test_session_factory, scope):
    from sqlalchemy import func, select

    from deja_platform_api.fotos.albums.models import (
        FotosAlbumModel,
        FotosAlbumPeriodDescriptionModel,
    )
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.models import FotosMediaModel
    from deja_platform_api.fotos.people.models import FotosPersonModel

    models = [
        FotosAlbumModel,
        FotosAlbumPeriodDescriptionModel,
        FotosPersonModel,
        FotosMediaModel,
        FotosFaceModel,
    ]
    with test_session_factory() as session:
        return tuple(
            session.scalar(
                select(func.count()).select_from(model).where(model.environment_id == scope["e"])
            )
            for model in models
        )


def test_pilot_initial_import_and_idempotent_rerun(
    migration_pilot_plan,
    test_session_factory,
    test_settings,
):
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.models import FotosMediaModel

    pilot = migration_pilot_plan
    first = _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert first["status"] == "completed"
    assert len(first["media"]) == 7
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (3, 1, 1, 7, 1)
    with test_session_factory() as session:
        photo = session.get(FotosMediaModel, pilot.plan["media"][0]["vivaro_id"])
        video = session.get(FotosMediaModel, pilot.plan["media"][-1]["vivaro_id"])
        face = session.get(
            FotosFaceModel,
            str(
                __import__("uuid").uuid5(
                    __import__("uuid").UUID(pilot.scope["e"]), "deja-album:face:241:0"
                )
            ),
        )
        assert photo.original_date is not None
        assert video.original_date is None
        assert face.status == "unknown" and face.person_id is None
    for item in pilot.plan["media"]:
        managed = test_settings.uploads_dir / item["storage_key"]
        assert managed.is_file()
        assert pilot.importer.file_sha256(managed) == item["source_sha256"]

    second = _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert second["status"] == "completed"
    assert len(second["media"]) == 7
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (3, 1, 1, 7, 1)
    assert len(pilot.process_calls) == 14


def test_pilot_resume_after_interrupted_derivatives(
    migration_pilot_plan,
    test_session_factory,
    test_settings,
):
    pilot = migration_pilot_plan
    pilot.failure_on["id"] = pilot.plan["media"][2]["vivaro_id"]
    with pytest.raises(RuntimeError, match="Falha simulada"):
        _apply_test_pilot(pilot, test_session_factory, test_settings)
    import json

    assert json.loads(pilot.report.read_text(encoding="utf-8"))["status"] == "partial_failure"
    assert _pilot_db_counts(test_session_factory, pilot.scope)[3] == 3

    pilot.failure_on["id"] = None
    result = _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert result["status"] == "completed"
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (3, 1, 1, 7, 1)


def test_pilot_rejects_changed_staged_file_before_writes(
    migration_pilot_plan,
    test_session_factory,
    test_settings,
):
    pilot = migration_pilot_plan
    staged = Path(pilot.plan["media"][4]["staged_file"])
    staged.write_bytes(staged.read_bytes() + b"TAMPERED")
    with pytest.raises(RuntimeError, match="Cópia do piloto inválida"):
        _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (0, 0, 0, 0, 0)


def test_pilot_integrated_real_image_and_video_derivatives(
    migration_pilot_plan,
    test_session_factory,
    test_settings,
    monkeypatch,
):
    """Exercita o importador e o processador REAL, com arquivos descartáveis."""
    import json
    import shutil
    from hashlib import sha256

    from deja_platform_api.fotos.media.derivative_service import FotosMediaDerivativeService
    from deja_platform_api.fotos.media.models import FotosMediaModel

    pilot = migration_pilot_plan
    assert test_settings.app_env == "testing"
    assert test_settings.db_name.endswith("_test")
    assert (
        shutil.which(test_settings.ffmpeg_executable)
        or Path(test_settings.ffmpeg_executable).is_file()
    )
    assert (
        shutil.which(test_settings.ffprobe_executable)
        or Path(test_settings.ffprobe_executable).is_file()
    )

    # A fixture usa conteúdo simulado para os vídeos nos testes de orquestração.
    # Neste teste, substituímos SOMENTE esses arquivos por MP4 H.264 reais.
    for entry in pilot.plan["media"]:
        if entry["media_type"] != "video":
            continue
        staged = Path(entry["staged_file"])
        subprocess.run(
            [
                test_settings.ffmpeg_executable,
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"{chr(116)}estsrc2=size=640x480:rate=15"
                if entry["legacy_id"] == 310
                else "testsrc=size=640x480:rate=15",
                "-t",
                "3.0",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                "-an",
                "-y",
                str(staged),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        entry["source_size"] = staged.stat().st_size
        entry["source_sha256"] = sha256(staged.read_bytes()).hexdigest()

    pilot.path.write_text(json.dumps(pilot.plan, ensure_ascii=False), encoding="utf-8")
    pilot.approved_hash = sha256(pilot.path.read_bytes()).hexdigest()

    # Desativa apenas as simulações da fixture para executar o serviço real.
    monkeypatch.setattr(FotosMediaDerivativeService, "process", _REAL_PROCESS)

    first = _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert first["status"] == "completed"
    assert len(first["media"]) == 7
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (3, 1, 1, 7, 1)

    with test_session_factory() as session:
        for entry in pilot.plan["media"]:
            record = session.get(FotosMediaModel, entry["vivaro_id"])
            assert record is not None
            assert record.processing_status == "ready", (
                entry["legacy_id"],
                record.processing_status,
                record.processing_error,
            )
            managed = test_settings.uploads_dir / record.original_storage_key
            assert managed.is_file(), managed
            assert pilot.importer.file_sha256(managed) == record.checksum_sha256

            # Inspeciona o diretório real de derivados sem depender da API HTTP.
            derivatives_dir = (
                test_settings.uploads_dir
                / "fotos"
                / pilot.scope["o"]
                / pilot.scope["t"]
                / pilot.scope["e"]
                / "derivatives"
            )
            assert derivatives_dir.is_dir(), derivatives_dir
            matches = list(derivatives_dir.rglob(f"{record.id}/*"))
            assert any(p.is_file() and p.stat().st_size > 0 for p in matches), (
                entry["legacy_id"],
                derivatives_dir,
            )

    # Reexecução após geração real dos derivados, inclusive vídeos normalizados.
    second = _apply_test_pilot(pilot, test_session_factory, test_settings)
    assert second["status"] == "completed"
    assert _pilot_db_counts(test_session_factory, pilot.scope) == (3, 1, 1, 7, 1)
