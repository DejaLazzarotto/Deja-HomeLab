/*
 * Deja Chamados
 *
 * Queue Board
 *
 * Quadro Kanban da Fila de Chamados.
 */

import {
  CdkDropListGroup,
} from '@angular/cdk/drag-drop';

import {
  ChangeDetectionStrategy,
  Component,
  computed,
  input,
  output,
} from '@angular/core';

import {
  Ticket,
  TicketStatus,
} from '../../../tickets';

import {
  QueueColumnComponent,
  QueueTicketMove,
} from '../queue-column/queue-column';

import {
  sortQueueTickets,
} from './queue-board.utils';

interface QueueColumnDefinition {
  readonly status: TicketStatus;
  readonly title: string;
}

const COLUMNS: readonly QueueColumnDefinition[] = [
  {
    status: 'open',
    title: 'Aberto',
  },
  {
    status: 'in_progress',
    title: 'Em andamento',
  },
  {
    status: 'pending',
    title: 'Pendente',
  },
  {
    status: 'closed',
    title: 'Fechado',
  },
];

@Component({
  selector: 'deja-queue-board',
  standalone: true,
  imports: [
    CdkDropListGroup,
    QueueColumnComponent,
  ],
  templateUrl: './queue-board.html',
  styleUrl: './queue-board.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class QueueBoardComponent {

  readonly tickets = input<readonly Ticket[]>([]);

  readonly clientNames =
    input<ReadonlyMap<string, string>>(new Map());

  readonly canManage = input(false);

  readonly updatingTicketId =
    input<string | null>(null);

  readonly ticketMoved =
    output<QueueTicketMove>();

  readonly columns = COLUMNS;

  readonly groupedTickets = computed(() => {
    const grouped = new Map<
      TicketStatus,
      readonly Ticket[]
    >();

    for (const column of COLUMNS) {
      grouped.set(
        column.status,
        sortQueueTickets(
          this.tickets(),
          column.status,
        ),
      );
    }

    return grouped;
  });

  ticketsFor(
    status: TicketStatus,
  ): readonly Ticket[] {
    return this.groupedTickets().get(status) ?? [];
  }

  onTicketMoved(
    event: QueueTicketMove,
  ): void {
    this.ticketMoved.emit(event);
  }


}
