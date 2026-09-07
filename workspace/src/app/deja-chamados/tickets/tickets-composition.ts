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
  TicketTimelineService,
  TicketService,
} from './application';

import {
  HttpTicketAssigneeRepository,
  HttpTicketTimelineRepository,
  HttpTicketRepository,
} from './infrastructure';

export class TicketsComposition {

  private readonly repository: HttpTicketRepository;

  private readonly timelineRepository:
    HttpTicketTimelineRepository;

  private readonly assigneeRepository:
    HttpTicketAssigneeRepository;

  readonly service: TicketService;

  readonly assigneeService: TicketAssigneeService;

  readonly timelineService: TicketTimelineService;

  constructor(
    http: HttpClient,
  ) {
    this.repository = new HttpTicketRepository(
      http,
    );

    this.timelineRepository =
      new HttpTicketTimelineRepository(
        http,
      );

    this.assigneeRepository =
      new HttpTicketAssigneeRepository(
        http,
      );

    this.service = new TicketService(
      this.repository,
    );

    this.timelineService =
      new TicketTimelineService(
        this.timelineRepository,
      );

    this.assigneeService =
      new TicketAssigneeService(
        this.assigneeRepository,
      );
  }

}