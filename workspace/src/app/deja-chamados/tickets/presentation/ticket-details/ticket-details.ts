/*
 * Deja Chamados
 *
 * Tickets Presentation
 *
 * Apresenta os detalhes administrativos de um chamado.
 */

import {
  DatePipe,
} from '@angular/common';

import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  input,
  output,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  TicketCommentService,
  TicketTimelineService,
  TicketService,
} from '../../application';

import {
  Ticket,
  TicketComment,
  TicketCommentVisibility,
  TicketTimelineEvent,
  TICKET_STATUS_TRANSITIONS,
  TicketStatus,
} from '../../domain';

@Component({
  selector: 'deja-ticket-details',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
  ],
  templateUrl: './ticket-details.html',
  styleUrl: './ticket-details.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TicketDetailsComponent implements OnInit {

  readonly ticketId = input.required<string>();

  readonly service = input.required<TicketService>();

  readonly timelineService =
    input.required<TicketTimelineService>();

  readonly commentService =
    input.required<TicketCommentService>();

  readonly canManage = input(false);

  readonly closed = output<void>();

  readonly ticket =
    signal<Ticket | null>(null);

  readonly timeline =
    signal<readonly TicketTimelineEvent[]>([]);

  readonly comments =
    signal<readonly TicketComment[]>([]);

  readonly commentMessage =
    signal('');

  readonly commentVisibility =
    signal<TicketCommentVisibility>('public');

  readonly loading =
    signal(false);

  readonly submittingComment =
    signal(false);

  readonly errorMessage =
    signal<string | null>(null);

  readonly commentErrorMessage =
    signal<string | null>(null);

  ngOnInit(): void {
    void this.loadDetails();
  }

  async loadDetails(): Promise<void> {
    if (this.loading()) {
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const ticketId = this.ticketId();

      const [
        ticket,
        timeline,
        comments,
      ] = await Promise.all([
        this.service().findById(
          ticketId,
        ),
        this.timelineService().listByTicketId(
          ticketId,
        ),
        this.commentService().listByTicketId(
          ticketId,
        ),
      ]);

      this.ticket.set(ticket);
      this.timeline.set(timeline);
      this.comments.set(comments);
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar os detalhes do chamado.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  onCommentMessageChange(
    value: string,
  ): void {
    this.commentMessage.set(value);
  }

  onCommentVisibilityChange(
    value: TicketCommentVisibility,
  ): void {
    this.commentVisibility.set(value);
  }

  async addComment(): Promise<void> {
    if (
      !this.canManage()
      || this.submittingComment()
    ) {
      return;
    }

    const ticket = this.ticket();
    const content = this.commentMessage().trim();

    if (
      !ticket
      || !content
    ) {
      return;
    }

    this.submittingComment.set(true);
    this.commentErrorMessage.set(null);

    try {
      await this.commentService().create(
        ticket.id,
        {
          content,
          visibility: this.commentVisibility(),
        },
      );

      const comments =
        await this.commentService().listByTicketId(
          ticket.id,
        );

      this.comments.set(comments);
      this.commentMessage.set('');
      this.commentVisibility.set('public');
    } catch {
      this.commentErrorMessage.set(
        'Não foi possível adicionar o comentário.',
      );
    } finally {
      this.submittingComment.set(false);
    }
  }

  back(): void {
    this.closed.emit();
  }

  statusLabel(
    status: Ticket['status'],
  ): string {
    switch (status) {
      case 'open':
        return 'Aberto';

      case 'in_progress':
        return 'Em andamento';

      case 'pending':
        return 'Pendente';

      case 'closed':
        return 'Encerrado';
    }
  }

  priorityLabel(
    priority: Ticket['priority'],
  ): string {
    switch (priority) {
      case 'low':
        return 'Baixa';

      case 'medium':
        return 'Média';

      case 'high':
        return 'Alta';

      case 'critical':
        return 'Crítica';
    }
  }

  visibilityLabel(
    visibility: TicketCommentVisibility,
  ): string {
    return visibility === 'public'
      ? 'Público'
      : 'Interno';
  }

  statusOptions(
    ticket: Ticket,
  ): readonly TicketStatus[] {
    return [
      ticket.status,
      ...TICKET_STATUS_TRANSITIONS[ticket.status],
    ];
  }

  async changeStatus(
    status: TicketStatus,
  ): Promise<void> {
    if (!this.canManage()) {
      return;
    }

    const ticket = this.ticket();

    if (
      !ticket
      || status === ticket.status
      || !TICKET_STATUS_TRANSITIONS[ticket.status].includes(status)
    ) {
      return;
    }

    this.errorMessage.set(null);

    try {
      await this.service().updateStatus(
        ticket.id,
        { status },
      );

      await this.loadDetails();
    } catch {
      this.errorMessage.set(
        'Não foi possível atualizar o status do chamado.',
      );
    }
  }

  timelineDescription(
    event: TicketTimelineEvent,
  ): string {
    if (
      event.eventType === 'status_changed'
      && event.previousValue
      && event.newValue
    ) {
      return `Status alterado de ${this.statusValueLabel(
        event.previousValue,
      )} para ${this.statusValueLabel(
        event.newValue,
      )}.`;
    }

    if (
      event.eventType === 'priority_changed'
      && event.previousValue
      && event.newValue
    ) {
      return `Prioridade alterada de ${this.priorityValueLabel(
        event.previousValue,
      )} para ${this.priorityValueLabel(
        event.newValue,
      )}.`;
    }

    if (event.eventType === 'assigned_changed') {
      const previous =
        event.previousDisplayValue
        ?? event.previousValue
        ?? 'sem responsável';

      const next =
        event.newDisplayValue
        ?? event.newValue
        ?? 'sem responsável';

      return `Responsável alterado de ${previous} para ${next}.`;
    }

    return event.description;
  }

  private statusValueLabel(
    value: string,
  ): string {
    switch (value) {
      case 'open':
        return 'Aberto';

      case 'in_progress':
        return 'Em andamento';

      case 'pending':
        return 'Pendente';

      case 'closed':
        return 'Encerrado';

      default:
        return value;
    }
  }

  private priorityValueLabel(
    value: string,
  ): string {
    switch (value) {
      case 'low':
        return 'Baixa';

      case 'medium':
        return 'Média';

      case 'high':
        return 'Alta';

      case 'critical':
        return 'Crítica';

      default:
        return value;
    }
  }

}