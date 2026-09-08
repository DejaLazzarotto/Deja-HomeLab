import {
  PortalTicket,
  PortalTicketCreate,
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

  create(
    input: PortalTicketCreate,
  ): Promise<PortalTicket> {
    return this.repository.create(input);
  }

}