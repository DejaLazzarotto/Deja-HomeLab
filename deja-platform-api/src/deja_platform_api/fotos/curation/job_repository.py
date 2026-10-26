"""Persistência da fila de reconhecimento facial do VIVARO."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
from deja_platform_api.fotos.media.models import FotosMediaModel


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class FotosFaceJobRepository:
    """Gerencia trabalhos faciais com transações no MySQL."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def enqueue(self, media: FotosMediaModel) -> FotosFaceJobModel | None:
        """Cadastra uma fotografia pronta sem duplicar o trabalho."""

        if (
            media.media_type != "image"
            or media.processing_status != "ready"
            or media.deleted_at is not None
        ):
            return None

        dialect = self.session.get_bind().dialect.name

        if dialect == "mysql":
            statement = (
                mysql_insert(FotosFaceJobModel)
                .values(
                    id=str(uuid4()),
                    media_id=media.id,
                    organization_id=media.organization_id,
                    tenant_id=media.tenant_id,
                    environment_id=media.environment_id,
                    status="pending",
                    attempts=0,
                    max_attempts=3,
                )
                .on_duplicate_key_update(id=FotosFaceJobModel.id)
            )
        elif dialect == "sqlite":
            statement = (
                sqlite_insert(FotosFaceJobModel)
                .values(
                    id=str(uuid4()),
                    media_id=media.id,
                    organization_id=media.organization_id,
                    tenant_id=media.tenant_id,
                    environment_id=media.environment_id,
                    status="pending",
                    attempts=0,
                    max_attempts=3,
                )
                .on_conflict_do_nothing(index_elements=["media_id"])
            )
        else:
            raise RuntimeError(f"Dialeto não suportado: {dialect}")

        self.session.execute(statement)
        self.session.flush()

        return self.session.scalar(
            select(FotosFaceJobModel).where(
                FotosFaceJobModel.media_id == media.id,
                FotosFaceJobModel.organization_id == media.organization_id,
                FotosFaceJobModel.tenant_id == media.tenant_id,
                FotosFaceJobModel.environment_id == media.environment_id,
            )
        )

    def claim_next(self) -> FotosFaceJobModel | None:
        """Reserva atomicamente o próximo trabalho disponível."""

        now = utc_now()

        statement = (
            select(FotosFaceJobModel)
            .join(
                FotosMediaModel,
                FotosFaceJobModel.media_id == FotosMediaModel.id,
            )
            .where(
                FotosFaceJobModel.status == "pending",
                FotosFaceJobModel.attempts < FotosFaceJobModel.max_attempts,
                or_(
                    FotosFaceJobModel.next_attempt_at.is_(None),
                    FotosFaceJobModel.next_attempt_at <= now,
                ),
                FotosMediaModel.processing_status == "ready",
                FotosMediaModel.media_type == "image",
                FotosMediaModel.deleted_at.is_(None),
                FotosFaceJobModel.organization_id == FotosMediaModel.organization_id,
                FotosFaceJobModel.tenant_id == FotosMediaModel.tenant_id,
                FotosFaceJobModel.environment_id == FotosMediaModel.environment_id,
            )
            .order_by(
                FotosFaceJobModel.created_at,
                FotosFaceJobModel.id,
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        job = self.session.scalar(statement)

        if job is None:
            return None

        job.claim_token = str(uuid4())
        job.status = "processing"
        job.attempts += 1
        job.started_at = now
        job.completed_at = None
        job.last_error = None
        job.next_attempt_at = None

        self.session.flush()

        return job

    def complete(self, job: FotosFaceJobModel, claim_token: str) -> None:
        """Conclui somente a tentativa que mantém a reserva válida."""

        result = self.session.execute(
            update(FotosFaceJobModel)
            .where(
                FotosFaceJobModel.id == job.id,
                FotosFaceJobModel.status == "processing",
                FotosFaceJobModel.claim_token == claim_token,
            )
            .values(
                status="completed",
                completed_at=utc_now(),
                last_error=None,
                next_attempt_at=None,
                claim_token=None,
            )
        )

        if result.rowcount != 1:
            raise RuntimeError("Reserva facial inválida ou expirada.")

        self.session.flush()

    def fail(
        self,
        job: FotosFaceJobModel,
        claim_token: str,
        error: str,
        *,
        retry_delay_seconds: int = 60,
    ) -> None:
        """Registra falha somente para a tentativa autorizada."""

        now = utc_now()
        exhausted = job.attempts >= job.max_attempts

        result = self.session.execute(
            update(FotosFaceJobModel)
            .where(
                FotosFaceJobModel.id == job.id,
                FotosFaceJobModel.status == "processing",
                FotosFaceJobModel.claim_token == claim_token,
                FotosFaceJobModel.attempts == job.attempts,
            )
            .values(
                status="failed" if exhausted else "pending",
                last_error=str(error)[:2000],
                completed_at=None,
                started_at=None,
                next_attempt_at=(
                    None if exhausted else now + timedelta(seconds=retry_delay_seconds)
                ),
                claim_token=None,
            )
        )

        if result.rowcount != 1:
            raise RuntimeError("Reserva facial inválida ou expirada.")

        self.session.flush()

    def recover_stale(
        self,
        *,
        timeout_minutes: int = 30,
    ) -> int:
        """Recupera trabalhos interrompidos sem ultrapassar tentativas."""

        if timeout_minutes <= 0:
            raise ValueError("O timeout deve ser positivo.")

        now = utc_now()
        stale_before = now - timedelta(minutes=timeout_minutes)

        statement = (
            select(FotosFaceJobModel)
            .where(
                FotosFaceJobModel.status == "processing",
                FotosFaceJobModel.started_at < stale_before,
            )
            .with_for_update(skip_locked=True)
        )

        jobs = self.session.scalars(statement).all()

        for job in jobs:
            job.last_error = "Processamento interrompido ou expirado."
            job.started_at = None
            job.claim_token = None

            if job.attempts >= job.max_attempts:
                job.status = "failed"
                job.next_attempt_at = None
            else:
                job.status = "pending"
                job.next_attempt_at = now

        self.session.flush()

        return len(jobs)

    def lock_valid_claim(self, job_id: str, claim_token: str) -> FotosFaceJobModel:
        """Bloqueia e valida a reserva antes de gravar resultados faciais."""

        job = self.session.scalar(
            select(FotosFaceJobModel)
            .where(
                FotosFaceJobModel.id == job_id,
                FotosFaceJobModel.status == "processing",
                FotosFaceJobModel.claim_token == claim_token,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        if job is None:
            raise RuntimeError("Reserva facial inválida ou expirada.")

        return job
