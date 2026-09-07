/*
 * Deja Chamados
 *
 * Queue Column
 *
 * Coluna de status da Fila de Chamados.
 */

import {
  CdkDrag,
  CdkDragDrop,
  CdkDropList,
} from '@angular/cdk/drag-drop';

import {
  ChangeDetectionStrategy,
  Component,
  input,
  output,
} from '@angular/core';

import {
  Ticket,
  TicketStatus,
} from '../../../tickets';

import {
  QueueTicketCardComponent,
} from '../queue-ticket-card/queue-ticket-card';

export interface QueueTicketMove {
  readonly ticket: Ticket;
  readonly status: TicketStatus;
}

@Component({
  selector: 'deja-queue-column',
  standalone: true,
  imports: [
    CdkDrag,
    CdkDropList,
    QueueTicketCardComponent,
  ],
  templateUrl: './queue-column.html',
  styleUrl: './queue-column.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class QueueColumnComponent {

  readonly status = input.required<TicketStatus>();

  readonly title = input.required<string>();

  readonly tickets = input<readonly Ticket[]>([]);

  readonly clientNames =
    input<ReadonlyMap<string, string>>(new Map());

  readonly canManage = input(false);

  readonly updatingTicketId =
    input<string | null>(null);

  readonly ticketMoved =
    output<QueueTicketMove>();

  clientName(
    clientId: string,
  ): string {
    return this.clientNames().get(clientId)
      ?? 'Cliente não identificado';
  }

  onDrop(
    event: CdkDragDrop<readonly Ticket[]>,
  ): void {
    if (!this.canManage()) {
      return;
    }

    const ticket = event.item.data as Ticket;

    if (ticket.status === this.status()) {
      return;
    }

    this.ticketMoved.emit({
      ticket,
      status: this.status(),
    });
  }

}
