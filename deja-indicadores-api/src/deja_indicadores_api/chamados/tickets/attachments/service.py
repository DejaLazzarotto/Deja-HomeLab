from pathlib import Path
from uuid import uuid7

from fastapi import UploadFile

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.tickets.attachments.exceptions import (
    ChamadosTicketAttachmentFileNotFoundError,
    ChamadosTicketAttachmentInvalidTypeError,
    ChamadosTicketAttachmentNotFoundError,
    ChamadosTicketAttachmentTooLargeError,
)
from deja_indicadores_api.chamados.tickets.attachments.models import (
    ChamadosTicketAttachmentModel,
)
from deja_indicadores_api.chamados.tickets.attachments.repository import (
    ChamadosTicketAttachmentRepository,
)
from deja_indicadores_api.chamados.tickets.attachments.schemas import (
    ChamadosTicketAttachmentResponse,
)
from deja_indicadores_api.chamados.tickets.exceptions import (
    ChamadosTicketNotFoundError,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.service import (
    CHAMADOS_TICKET_OPERATOR_ROLES,
    CHAMADOS_TICKET_READER_ROLES,
)
from deja_indicadores_api.chamados.tickets.timeline.service import (
    ChamadosTicketTimelineService,
)
from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

ALLOWED_ATTACHMENT_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/pdf",
}


class ChamadosTicketAttachmentService:
    """Regras de aplicação dos anexos de chamados."""

    def __init__(
        self,
        repository: ChamadosTicketAttachmentRepository,
        ticket_repository: ChamadosTicketRepository,
        timeline_service: ChamadosTicketTimelineService,
        authorization_service: AuthorizationService,
        user_repository: UserRepository,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._ticket_repository = ticket_repository
        self._timeline_service = timeline_service
        self._authorization_service = authorization_service
        self._user_repository = user_repository
        self._settings = settings

    def list_by_ticket_id(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> list[ChamadosTicketAttachmentResponse]:
        """Lista anexos de um chamado autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_READER_ROLES,
        )

        ticket = self._require_ticket(ticket_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        attachments = self._repository.list_by_ticket_id(
            ticket_id,
        )

        return [
            self._map_attachment(attachment)
            for attachment in attachments
        ]

    async def create_from_upload(
        self,
        ticket_id: str,
        file: UploadFile,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketAttachmentResponse:
        """Armazena e registra um novo anexo em chamado autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_OPERATOR_ROLES,
        )

        ticket = self._require_ticket(ticket_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        content_type = file.content_type or "application/octet-stream"

        if content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
            raise ChamadosTicketAttachmentInvalidTypeError(
                content_type,
            )

        content = await file.read()

        max_size_bytes = (
            self._settings.ticket_attachment_max_size_mb
            * 1024
            * 1024
        )

        if len(content) > max_size_bytes:
            raise ChamadosTicketAttachmentTooLargeError(
                self._settings.ticket_attachment_max_size_mb,
            )

        original_name = Path(
            file.filename or "arquivo"
        ).name

        extension = Path(original_name).suffix.lower()
        attachment_id = str(uuid7())
        stored_file_name = f"{attachment_id}{extension}"

        upload_dir = (
            self._settings.uploads_dir
            / "chamados"
            / "tickets"
            / ticket.id
        )
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = upload_dir / stored_file_name
        file_path.write_bytes(content)

        attachment = ChamadosTicketAttachmentModel(
            id=attachment_id,
            ticket_id=ticket.id,
            file_name=stored_file_name,
            original_name=original_name,
            content_type=content_type,
            file_size=len(content),
            file_path=str(file_path),
            created_by_user_id=current_user.id,
        )

        self._repository.add(attachment)

        self._timeline_service.register(
            ticket_id=ticket.id,
            event_type="attachment_added",
            description=f"Anexo adicionado: {original_name}",
            created_by_user_id=current_user.id,
            new_value=attachment.id,
        )

        saved_attachment = self._repository.commit(
            attachment,
        )

        if saved_attachment is None:
            raise RuntimeError(
                "Falha ao persistir o anexo do chamado."
            )

        return self._map_attachment(
            saved_attachment,
        )

    def get_download_file(
        self,
        attachment_id: str,
        current_user: AuthenticatedUser,
    ) -> tuple[Path, ChamadosTicketAttachmentModel]:
        """Retorna o arquivo físico de um anexo autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_READER_ROLES,
        )

        attachment = self._require_attachment(
            attachment_id,
        )

        ticket = self._require_ticket(
            attachment.ticket_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        file_path = Path(
            attachment.file_path,
        )

        if not file_path.exists() or not file_path.is_file():
            raise ChamadosTicketAttachmentFileNotFoundError(
                attachment.id,
            )

        return file_path, attachment

    def delete(
        self,
        attachment_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Remove um anexo de chamado autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_OPERATOR_ROLES,
        )

        attachment = self._require_attachment(
            attachment_id,
        )

        ticket = self._require_ticket(
            attachment.ticket_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        file_path = Path(
            attachment.file_path,
        )

        self._repository.delete(
            attachment,
        )

        self._timeline_service.register(
            ticket_id=ticket.id,
            event_type="attachment_removed",
            description=f"Anexo removido: {attachment.original_name}",
            created_by_user_id=current_user.id,
            previous_value=attachment.id,
        )

        self._repository.commit()

        if file_path.exists() and file_path.is_file():
            file_path.unlink()

    def _map_attachment(
        self,
        attachment: ChamadosTicketAttachmentModel,
    ) -> ChamadosTicketAttachmentResponse:
        """Converte anexo persistido para resposta pública."""

        return ChamadosTicketAttachmentResponse(
            id=attachment.id,
            ticket_id=attachment.ticket_id,
            original_name=attachment.original_name,
            content_type=attachment.content_type,
            file_size=attachment.file_size,
            created_by_user_id=attachment.created_by_user_id,
            created_by=self._resolve_user_name(
                attachment.created_by_user_id,
            ),
            created_at=attachment.created_at,
        )

    def _resolve_user_name(
        self,
        user_id: str | None,
    ) -> str | None:
        """Resolve o nome do usuário que adicionou o anexo."""

        if user_id is None:
            return None

        user = self._user_repository.find_by_id(
            user_id,
        )

        if user is None:
            return None

        return user.name

    def _require_ticket(
        self,
        ticket_id: str,
    ):
        """Retorna um chamado existente."""

        ticket = self._ticket_repository.find_by_id(
            ticket_id,
        )

        if ticket is None:
            raise ChamadosTicketNotFoundError(
                ticket_id,
            )

        return ticket

    def _require_attachment(
        self,
        attachment_id: str,
    ) -> ChamadosTicketAttachmentModel:
        """Retorna um anexo existente."""

        attachment = self._repository.find_by_id(
            attachment_id,
        )

        if attachment is None:
            raise ChamadosTicketAttachmentNotFoundError(
                attachment_id,
            )

        return attachment