from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChamadosTicketAttachmentResponse(BaseModel):
    """Representação pública de um anexo de chamado."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    original_name: str
    content_type: str
    file_size: int
    created_by_user_id: str | None
    created_by: str | None
    created_at: datetime