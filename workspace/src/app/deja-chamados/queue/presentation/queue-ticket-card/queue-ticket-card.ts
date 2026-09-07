/*
 * Deja Chamados
 *
 * Queue Ticket Card
 *
 * Cartão visual de um chamado dentro da Fila.
 */

import {
  ChangeDetectionStrategy,
  Component,
  input,
} from '@angular/core';

import {
  Ticket,
  TicketPriority,
  TicketStatus,
} from '../../../tickets';

@Component({
  selector: 'deja-queue-ticket-card',
  standalone: true,
  templateUrl: './queue-ticket-card.html',
  styleUrl: './queue-ticket-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class QueueTicketCardComponent {

  readonly ticket = input.required<Ticket>();

  readonly clientName = input.required<string>();

  statusLabel(
    status: TicketStatus,
  ): string {
    const labels: Record<TicketStatus, string> = {
      open: 'Aberto',
      in_progress: 'Em andamento',
      pending: 'Pendente',
      closed: 'Fechado',
    };

    return labels[status];
  }

  priorityLabel(
    priority: TicketPriority,
  ): string {
    const labels: Record<TicketPriority, string> = {
      low: 'Baixa',
      medium: 'Média',
      high: 'Alta',
      critical: 'Crítica',
    };

    return labels[priority];
  }

  formatDate(
    value: string,
  ): string {
    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(new Date(value));
  }

}
