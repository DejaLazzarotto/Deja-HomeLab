from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import FileResponse

from deja_indicadores_api.authentication.dependencies import (
    require_roles,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.portal.dependencies import (
    ChamadosPortalServiceDependency,
)
from deja_indicadores_api.chamados.portal.schemas import (
    ChamadosPortalAttachmentResponse,
    ChamadosPortalCommentCreate,
    ChamadosPortalCommentResponse,
    ChamadosPortalTicketCreate,
    ChamadosPortalTicketResponse,
    ChamadosPortalTimelineResponse,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import (
    UserRole,
)

router = APIRouter(
    prefix="/chamados/portal",
    tags=["Deja Chamados - Portal"],
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


ChamadosPortalUser = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.CLIENT,
        )
    ),
]


@router.get(
    "/tickets",
    response_model=list[ChamadosPortalTicketResponse],
)
def list_portal_tickets(
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> list[ChamadosPortalTicketResponse]:
    """Lista somente os chamados do Cliente autenticado."""

    return service.list_tickets(
        current_user,
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=ChamadosPortalTicketResponse,
)
def get_portal_ticket(
    ticket_id: TicketId,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> ChamadosPortalTicketResponse:
    """Consulta um chamado pertencente ao Cliente autenticado."""

    return service.find_ticket_by_id(
        ticket_id,
        current_user,
    )


@router.get(
    "/tickets/{ticket_id}/timeline",
    response_model=list[ChamadosPortalTimelineResponse],
)
def list_portal_ticket_timeline(
    ticket_id: TicketId,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> list[ChamadosPortalTimelineResponse]:
    """Lista o histórico seguro de um chamado do Cliente autenticado."""

    return service.list_ticket_timeline(
        ticket_id,
        current_user,
    )


@router.get(
    "/tickets/{ticket_id}/comments",
    response_model=list[ChamadosPortalCommentResponse],
)
def list_portal_ticket_comments(
    ticket_id: TicketId,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> list[ChamadosPortalCommentResponse]:
    """Lista os comentários públicos de um chamado do Cliente."""

    return service.list_ticket_comments(
        ticket_id,
        current_user,
    )


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=ChamadosPortalCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portal_ticket_comment(
    ticket_id: TicketId,
    input_data: ChamadosPortalCommentCreate,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> ChamadosPortalCommentResponse:
    """Adiciona um comentário público a um chamado do Cliente."""

    return service.create_ticket_comment(
        ticket_id,
        input_data,
        current_user,
    )


@router.get(
    "/tickets/{ticket_id}/attachments",
    response_model=list[ChamadosPortalAttachmentResponse],
)
def list_portal_ticket_attachments(
    ticket_id: TicketId,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> list[ChamadosPortalAttachmentResponse]:
    """Lista anexos de um chamado pertencente ao Cliente autenticado."""

    return service.list_ticket_attachments(
        ticket_id,
        current_user,
    )


@router.get(
    "/attachments/{attachment_id}/download",
)
def download_portal_ticket_attachment(
    attachment_id: AttachmentId,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> FileResponse:
    """Baixa um anexo pertencente a chamado do Cliente autenticado."""

    file_path, attachment = service.get_ticket_attachment_download(
        attachment_id,
        current_user,
    )

    return FileResponse(
        path=file_path,
        filename=attachment.original_name,
        media_type=attachment.content_type,
    )


@router.post(
    "/tickets",
    response_model=ChamadosPortalTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portal_ticket(
    input_data: ChamadosPortalTicketCreate,
    service: ChamadosPortalServiceDependency,
    current_user: ChamadosPortalUser,
) -> ChamadosPortalTicketResponse:
    """Abre um novo chamado para o Cliente autenticado."""

    return service.create_ticket(
        input_data,
        current_user,
    )