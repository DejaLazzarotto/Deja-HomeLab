from pydantic import BaseModel, ConfigDict

from deja_indicadores_api.user_management.models import UserRole


class ChamadosTicketAssigneeResponse(BaseModel):
    """Representação pública de um responsável elegível."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: UserRole