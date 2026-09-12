from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Path,
    UploadFile,
)
from fastapi import status as http_status
from fastapi.responses import FileResponse

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.attachments.dependencies import (
    ChamadosTicketAttachmentServiceDependency,
)
from deja_indicadores_api.chamados.tickets.attachments.schemas import (
    ChamadosTicketAttachmentResponse,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/chamados/tickets",
    tags=["Deja Chamados - Anexos"],
    dependencies=[Depends(require_module("chamados"))],
)


TicketId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do chamado.",
    ),
]


AttachmentId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do anexo.",
    ),
]


AttachmentFile = Annotated[
    UploadFile,
    File(),
]


ChamadosTicketAttachmentReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]


ChamadosTicketAttachmentOperator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
        )
    ),
]


@router.get(
    "/{ticket_id}/attachments",
    response_model=list[ChamadosTicketAttachmentResponse],
)
def list_ticket_attachments(
    ticket_id: TicketId,
    service: ChamadosTicketAttachmentServiceDependency,
    current_user: ChamadosTicketAttachmentReader,
) -> list[ChamadosTicketAttachmentResponse]:
    """Lista os anexos de um chamado autorizado."""

    return service.list_by_ticket_id(
        ticket_id,
        current_user,
    )


@router.post(
    "/{ticket_id}/attachments",
    response_model=ChamadosTicketAttachmentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def upload_ticket_attachment(
    ticket_id: TicketId,
    service: ChamadosTicketAttachmentServiceDependency,
    current_user: ChamadosTicketAttachmentOperator,
    file: AttachmentFile,
) -> ChamadosTicketAttachmentResponse:
    """Adiciona um anexo a um chamado autorizado."""

    return await service.create_from_upload(
        ticket_id,
        file,
        current_user,
    )


@router.get(
    "/attachments/{attachment_id}/download",
)
def download_ticket_attachment(
    attachment_id: AttachmentId,
    service: ChamadosTicketAttachmentServiceDependency,
    current_user: ChamadosTicketAttachmentReader,
) -> FileResponse:
    """Baixa um anexo de chamado autorizado."""

    file_path, attachment = service.get_download_file(
        attachment_id,
        current_user,
    )

    return FileResponse(
        path=file_path,
        filename=attachment.original_name,
        media_type=attachment.content_type,
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_ticket_attachment(
    attachment_id: AttachmentId,
    service: ChamadosTicketAttachmentServiceDependency,
    current_user: ChamadosTicketAttachmentOperator,
) -> None:
    """Remove um anexo de chamado autorizado."""

    service.delete(
        attachment_id,
        current_user,
    )