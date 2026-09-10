import {
  DatePipe,
} from '@angular/common';

import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  HttpClient,
} from '@angular/common/http';

import {
  PortalTicket,
  PortalTicketComment,
  PortalTimelineEvent,
} from '../../domain/portal-ticket';

import {
  PortalComposition,
} from '../../portal-composition';

@Component({
  selector: 'deja-portal-ticket-details',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
  ],
  templateUrl: './portal-ticket-details.html',
  styleUrl: './portal-ticket-details.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PortalTicketDetailsComponent implements OnInit {
  private readonly route =
    inject(ActivatedRoute);

  private readonly router =
    inject(Router);

  private readonly http =
    inject(HttpClient);

  private readonly composition =
    new PortalComposition(
      this.http,
    );

  readonly ticket =
    signal<PortalTicket | null>(null);

  readonly timeline =
    signal<readonly PortalTimelineEvent[]>([]);

  readonly comments =
    signal<readonly PortalTicketComment[]>([]);

  readonly commentMessage =
    signal('');

  readonly loading =
    signal(false);

  readonly submittingComment =
    signal(false);

  readonly errorMessage =
    signal('');

  readonly commentErrorMessage =
    signal('');

  ngOnInit(): void {
    void this.loadDetails();
  }

  async loadDetails(): Promise<void> {
    if (this.loading()) {
      return;
    }

    const ticketId =
      this.route.snapshot.paramMap.get('id');

    if (!ticketId) {
      this.errorMessage.set(
        'Chamado não informado.',
      );

      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');

    try {
      const [
        ticket,
        timeline,
        comments,
      ] = await Promise.all([
        this.composition.service.findById(
          ticketId,
        ),
        this.composition.service.listTimeline(
          ticketId,
        ),
        this.composition.service.listComments(
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

  async addComment(): Promise<void> {
    if (this.submittingComment()) {
      return;
    }

    const ticket = this.ticket();
    const content = this.commentMessage().trim();

    if (!ticket || !content) {
      return;
    }

    this.submittingComment.set(true);
    this.commentErrorMessage.set('');

    try {
      await this.composition.service.createComment(
        ticket.id,
        {
          content,
        },
      );

      const comments =
        await this.composition.service.listComments(
          ticket.id,
        );

      this.comments.set(comments);
      this.commentMessage.set('');
    } catch {
      this.commentErrorMessage.set(
        'Não foi possível adicionar o comentário.',
      );
    } finally {
      this.submittingComment.set(false);
    }
  }

  back(): void {
    void this.router.navigate([
      '/portal',
    ]);
  }

  statusLabel(
    status: PortalTicket['status'],
  ): string {
    switch (status) {
      case 'open':
        return 'Aberto';

      case 'in_progress':
        return 'Em andamento';

      case 'pending':
        return 'Pendente';

      case 'closed':
        return 'Fechado';
    }
  }

  priorityLabel(
    priority: PortalTicket['priority'],
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

  timelineDescription(
    event: PortalTimelineEvent,
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
        event.previousValue ?? 'sem responsável';

      const next =
        event.newValue ?? 'sem responsável';

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
        return 'Fechado';

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