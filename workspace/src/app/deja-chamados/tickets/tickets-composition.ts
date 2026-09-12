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
  TicketAttachmentService,
  TicketCommentService,
  TicketTimelineService,
  TicketService,
} from './application';

import {
  HttpTicketAssigneeRepository,
  HttpTicketAttachmentRepository,
  HttpTicketCommentRepository,
  HttpTicketTimelineRepository,
  HttpTicketRepository,
} from './infrastructure';

export class TicketsComposition {

  private readonly repository: HttpTicketRepository;

  private readonly timelineRepository:
    HttpTicketTimelineRepository;

  private readonly assigneeRepository:
    HttpTicketAssigneeRepository;

  private readonly commentRepository:
    HttpTicketCommentRepository;

  private readonly attachmentRepository:
    HttpTicketAttachmentRepository;

  readonly service: TicketService;

  readonly assigneeService: TicketAssigneeService;

  readonly timelineService: TicketTimelineService;

  readonly commentService: TicketCommentService;

  readonly attachmentService: TicketAttachmentService;

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

    this.commentRepository =
      new HttpTicketCommentRepository(
        http,
      );

    this.attachmentRepository =
      new HttpTicketAttachmentRepository(
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

    this.commentService =
      new TicketCommentService(
        this.commentRepository,
      );

    this.attachmentService =
      new TicketAttachmentService(
        this.attachmentRepository,
      );
  }

}