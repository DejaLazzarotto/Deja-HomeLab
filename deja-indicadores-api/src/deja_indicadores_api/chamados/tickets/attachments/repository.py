from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.tickets.attachments.models import (
    ChamadosTicketAttachmentModel,
)


class ChamadosTicketAttachmentRepository:
    """Persistência dos anexos de chamados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[ChamadosTicketAttachmentModel]:
        """Lista anexos de um chamado em ordem cronológica."""

        statement = (
            select(ChamadosTicketAttachmentModel)
            .where(
                ChamadosTicketAttachmentModel.ticket_id == ticket_id
            )
            .order_by(
                ChamadosTicketAttachmentModel.created_at.asc(),
                ChamadosTicketAttachmentModel.id.asc(),
            )
        )

        return list(
            self._session.scalars(statement).all()
        )

    def find_by_id(
        self,
        attachment_id: str,
    ) -> ChamadosTicketAttachmentModel | None:
        """Busca um anexo pelo identificador."""

        statement = select(
            ChamadosTicketAttachmentModel
        ).where(
            ChamadosTicketAttachmentModel.id == attachment_id
        )

        return self._session.scalar(statement)

    def add(
        self,
        attachment: ChamadosTicketAttachmentModel,
    ) -> ChamadosTicketAttachmentModel:
        """Adiciona um anexo à sessão."""

        self._session.add(attachment)
        return attachment

    def delete(
        self,
        attachment: ChamadosTicketAttachmentModel,
    ) -> None:
        """Marca um anexo para exclusão."""

        self._session.delete(attachment)

    def commit(
        self,
        attachment: ChamadosTicketAttachmentModel | None = None,
    ) -> ChamadosTicketAttachmentModel | None:
        """Persiste a transação atual."""

        self._session.commit()

        if attachment is not None:
            self._session.refresh(attachment)

        return attachment