/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Representa um anexo associado a um chamado.
 */

export type TicketAttachmentContentType =
  | 'image/png'
  | 'image/jpeg'
  | 'image/webp'
  | 'application/pdf';

export interface TicketAttachment {
  readonly id: string;
  readonly ticketId: string;
  readonly originalName: string;
  readonly contentType: TicketAttachmentContentType;
  readonly fileSize: number;
  readonly createdByUserId: string | null;
  readonly createdBy: string | null;
  readonly createdAt: string;
}