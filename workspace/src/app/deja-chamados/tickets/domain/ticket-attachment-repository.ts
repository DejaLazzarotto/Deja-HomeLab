/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Contrato de acesso aos anexos dos chamados.
 */

import { TicketAttachment } from './ticket-attachment';

export interface TicketAttachmentRepository {
  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketAttachment[]>;

  upload(
    ticketId: string,
    file: File,
  ): Promise<TicketAttachment>;

  delete(
    attachmentId: string,
  ): Promise<void>;

  download(
    attachmentId: string,
  ): Promise<Blob>;
}