/*
 * Deja Chamados
 *
 * Queue Management
 *
 * Coordena o carregamento e a atualização da Fila de Chamados.
 */

import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  computed,
  input,
  signal,
} from '@angular/core';

import {
  Client,
} from '../../../clients';

import {
  Ticket,
  TicketService,
  TicketStatus,
} from '../../../tickets';

import {
  QueueBoardComponent,
} from '../queue-board/queue-board';

import {
  QueueTicketMove,
} from '../queue-column/queue-column';

@Component({
  selector: 'deja-queue-management',
  standalone: true,
  imports: [
    QueueBoardComponent,
  ],
  templateUrl: './queue-management.html',
  styleUrl: './queue-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class QueueManagementComponent
implements OnInit {

  readonly service = input.required<TicketService>();

  readonly clients = input<readonly Client[]>([]);

  readonly canManage = input(false);

  readonly tickets = signal<readonly Ticket[]>([]);

  readonly loading = signal(false);

  readonly updatingTicketId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);

  readonly clientNames = computed(() => {
    const names = new Map<string, string>();

    for (const client of this.clients()) {
      names.set(
        client.id,
        client.fantasyName
        || client.companyName
        || 'Cliente não identificado',
      );
    }

    return names;
  });

  ngOnInit(): void {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      this.tickets.set(
        await this.service().list(),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar a fila de chamados.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  async onTicketMoved(
    event: QueueTicketMove,
  ): Promise<void> {
    if (
      !this.canManage()
      || this.updatingTicketId()
      || event.ticket.status === event.status
    ) {
      return;
    }

    const previousTickets = this.tickets();

    this.operationError.set(null);
    this.operationMessage.set(null);
    this.updatingTicketId.set(event.ticket.id);

    this.tickets.update(tickets =>
      tickets.map(ticket =>
        ticket.id === event.ticket.id
          ? {
              ...ticket,
              status: event.status,
            }
          : ticket,
      ),
    );

    try {
      const updatedTicket =
        await this.service().updateStatus(
          event.ticket.id,
          {
            status: event.status,
          },
        );

      this.tickets.update(tickets =>
        tickets.map(ticket =>
          ticket.id === updatedTicket.id
            ? updatedTicket
            : ticket,
        ),
      );

      this.operationMessage.set(
        this.successMessage(
          event.ticket.status,
          event.status,
        ),
      );
    } catch (error: unknown) {
      this.tickets.set(previousTickets);

      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.updatingTicketId.set(null);
    }
  }

  private successMessage(
    previousStatus: TicketStatus,
    status: TicketStatus,
  ): string {
    if (status === 'closed') {
      return 'Chamado encerrado com sucesso.';
    }

    if (
      status === 'open'
      && previousStatus === 'closed'
    ) {
      return 'Chamado reaberto com sucesso.';
    }

    return 'Status atualizado com sucesso.';
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível atualizar o chamado.';
    }

    if (error.status === 0) {
      return 'Não foi possível acessar a API.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O chamado não foi encontrado.';
    }

    if (error.status === 409) {
      return 'A operação conflita com o estado atual do chamado.';
    }

    if (error.status === 422) {
      return 'A mudança de status informada não é válida.';
    }

    return 'Não foi possível atualizar o chamado.';
  }

}
