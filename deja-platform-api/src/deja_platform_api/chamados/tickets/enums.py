from enum import StrEnum


class ChamadosTicketStatus(StrEnum):
    """Estados permitidos para um chamado."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    CLOSED = "closed"


class ChamadosTicketPriority(StrEnum):
    """Prioridades permitidas para um chamado."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"