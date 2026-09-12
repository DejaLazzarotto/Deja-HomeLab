/*
 * Deja Chamados
 *
 * Tickets Infrastructure
 *
 * Repositório HTTP responsável pelos anexos dos chamados.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  TicketAttachment,
  TicketAttachmentContentType,
  TicketAttachmentRepository,
} from '../domain';

interface TicketAttachmentResponse {
  readonly id: string;
  readonly ticket_id: string;
  readonly original_name: string;
  readonly content_type: TicketAttachmentContentType;
  readonly file_size: number;
  readonly created_by_user_id: string | null;
  readonly created_by: string | null;
  readonly created_at: string;
}

export class HttpTicketAttachmentRepository
implements TicketAttachmentRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketAttachment[]> {
    const response = await firstValueFrom(
      this.http.get<readonly TicketAttachmentResponse[]>(
        `/api/chamados/tickets/${ticketId}/attachments`,
      ),
    );

    return response.map(
      attachment => this.mapAttachment(attachment),
    );
  }

  async upload(
    ticketId: string,
    file: File,
  ): Promise<TicketAttachment> {
    const formData = new FormData();

    formData.append(
      'file',
      file,
    );

    const response = await firstValueFrom(
      this.http.post<TicketAttachmentResponse>(
        `/api/chamados/tickets/${ticketId}/attachments`,
        formData,
      ),
    );

    return this.mapAttachment(response);
  }

  async delete(
    attachmentId: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/chamados/tickets/attachments/${attachmentId}`,
      ),
    );
  }

  async download(
    attachmentId: string,
  ): Promise<Blob> {
    return firstValueFrom(
      this.http.get(
        `/api/chamados/tickets/attachments/${attachmentId}/download`,
        {
          responseType: 'blob',
        },
      ),
    );
  }

  private mapAttachment(
    attachment: TicketAttachmentResponse,
  ): TicketAttachment {
    return {
      id: attachment.id,
      ticketId: attachment.ticket_id,
      originalName: attachment.original_name,
      contentType: attachment.content_type,
      fileSize: attachment.file_size,
      createdByUserId: attachment.created_by_user_id,
      createdBy: attachment.created_by,
      createdAt: attachment.created_at,
    };
  }

}