/*
 * Deja Chamados
 *
 * Tickets Application
 *
 * Serviço responsável por coordenar os anexos dos chamados.
 */

import {
  TicketAttachment,
  TicketAttachmentRepository,
} from '../domain';

export class TicketAttachmentService {

  constructor(
    private readonly repository: TicketAttachmentRepository,
  ) {}

  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketAttachment[]> {
    return this.repository.listByTicketId(
      ticketId,
    );
  }

  upload(
    ticketId: string,
    file: File,
  ): Promise<TicketAttachment> {
    return this.repository.upload(
      ticketId,
      file,
    );
  }

  delete(
    attachmentId: string,
  ): Promise<void> {
    return this.repository.delete(
      attachmentId,
    );
  }

  download(
    attachmentId: string,
  ): Promise<Blob> {
    return this.repository.download(
      attachmentId,
    );
  }

}