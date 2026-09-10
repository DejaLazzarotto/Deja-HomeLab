import {
  PortalTicket,
  PortalTicketComment,
  PortalTicketCommentCreate,
  PortalTicketCreate,
  PortalTimelineEvent,
} from '../domain/portal-ticket';

import {
  HttpPortalTicketRepository,
} from '../infrastructure/http-portal-ticket-repository';

export class PortalTicketNotFoundError extends Error {

  constructor(
    readonly ticketId: string,
  ) {
    super(
      `Chamado ${ticketId} não foi encontrado no Portal.`,
    );

    this.name = 'PortalTicketNotFoundError';
  }

}

export class PortalTicketService {

  constructor(
    private readonly repository: HttpPortalTicketRepository,
  ) {}

  list(): Promise<readonly PortalTicket[]> {
    return this.repository.list();
  }

  async findById(
    id: string,
  ): Promise<PortalTicket> {
    const ticket = await this.repository.findById(id);

    if (!ticket) {
      throw new PortalTicketNotFoundError(id);
    }

    return ticket;
  }

  listTimeline(
    ticketId: string,
  ): Promise<readonly PortalTimelineEvent[]> {
    return this.repository.listTimeline(ticketId);
  }

  listComments(
    ticketId: string,
  ): Promise<readonly PortalTicketComment[]> {
    return this.repository.listComments(ticketId);
  }

  createComment(
    ticketId: string,
    input: PortalTicketCommentCreate,
  ): Promise<PortalTicketComment> {
    return this.repository.createComment(
      ticketId,
      input,
    );
  }

  create(
    input: PortalTicketCreate,
  ): Promise<PortalTicket> {
    return this.repository.create(input);
  }

}