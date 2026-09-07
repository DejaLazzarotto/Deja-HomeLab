from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChamadosTicketTimelineResponse(BaseModel):
    """Representação pública de um evento do histórico do chamado."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    event_type: str
    description: str
    previous_value: str | None
    new_value: str | None
    created_by_user_id: str | None
    created_at: datetime
