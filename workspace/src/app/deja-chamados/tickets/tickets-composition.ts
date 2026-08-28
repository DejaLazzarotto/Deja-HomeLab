/*
 * Deja Chamados
 *
 * Tickets Composition
 *
 * Composição das dependências da Gestão de Chamados.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  TicketAssigneeService,
  TicketService,
} from './application';

import {
  HttpTicketAssigneeRepository,
  HttpTicketRepository,
} from './infrastructure';

export class TicketsComposition {

  private readonly repository: HttpTicketRepository;

  private readonly assigneeRepository:
    HttpTicketAssigneeRepository;

  readonly service: TicketService;

  readonly assigneeService: TicketAssigneeService;

  constructor(
    http: HttpClient,
  ) {
    this.repository = new HttpTicketRepository(
      http,
    );

    this.assigneeRepository =
      new HttpTicketAssigneeRepository(
        http,
      );

    this.service = new TicketService(
      this.repository,
    );

    this.assigneeService =
      new TicketAssigneeService(
        this.assigneeRepository,
      );
  }

}