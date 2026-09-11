/*
 * Deja Chamados
 *
 * Tickets Presentation
 *
 * Coordena a consulta e o gerenciamento visual dos chamados.
 */

import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  input,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  Client,
} from '../../../clients';

import {
  TicketAssigneeService,
  TicketCommentService,
  TicketService,
  TicketTimelineService,
} from '../../application';

import {
  Ticket,
  TicketAssignee,
  TicketCreateInput,
  TicketFilters,
  TicketPriority,
  TicketStatus,
  TicketUpdateInput,
} from '../../domain';

import {
  TicketDetailsComponent,
} from '../ticket-details/ticket-details';

type TicketStatusFilter =
  | 'all'
  | TicketStatus;

type TicketPriorityFilter =
  | 'all'
  | TicketPriority;

interface TicketDraft {
  readonly clientId: string;
  readonly title: string;
  readonly description: string;
  readonly priority: TicketPriority;
  readonly assignedToUserId: string | null;
}

const EMPTY_DRAFT: TicketDraft = {
  clientId: '',
  title: '',
  description: '',
  priority: 'medium',
  assignedToUserId: null,
};

const STATUS_TRANSITIONS: Readonly<
  Record<TicketStatus, readonly TicketStatus[]>
> = {
  open: [
    'in_progress',
    'pending',
    'closed',
  ],
  in_progress: [
    'open',
    'pending',
    'closed',
  ],
  pending: [
    'open',
    'in_progress',
    'closed',
  ],
  closed: [
    'open',
  ],
};

@Component({
  selector: 'deja-ticket-management',
  standalone: true,
  imports: [
    FormsModule,
    TicketDetailsComponent,
  ],
  templateUrl: './ticket-management.html',
  styleUrl: './ticket-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TicketManagementComponent
implements OnInit, OnDestroy {

  readonly service = input.required<TicketService>();

  readonly assigneeService =
    input.required<TicketAssigneeService>();

  readonly timelineService =
    input.required<TicketTimelineService>();

  readonly commentService =
    input.required<TicketCommentService>();

  readonly clients = input<readonly Client[]>([]);

  readonly canManage = input(false);

  readonly tickets = signal<readonly Ticket[]>([]);

  readonly searchTerm = signal('');

  readonly clientFilter = signal('all');

  readonly statusFilter =
    signal<TicketStatusFilter>('all');

  readonly priorityFilter =
    signal<TicketPriorityFilter>('all');

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly changingStatusTicketId =
    signal<string | null>(null);

  readonly loadingAssignees = signal(false);

  readonly selectedTicket = signal<Ticket | null>(null);

  readonly draft = signal<TicketDraft>(EMPTY_DRAFT);

  readonly assignees =
    signal<readonly TicketAssignee[]>([]);

  readonly formVisible = signal(false);

  readonly errorMessage = signal<string | null>(null);

  readonly operationMessage = signal<string | null>(null);

  readonly operationError = signal<string | null>(null);

  readonly detailsTicketId =
    signal<string | null>(null);

  private readonly assigneesByClient =
    new Map<string, readonly TicketAssignee[]>();

  private readonly assigneeNames =
    new Map<string, string>();

  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  private requestSequence = 0;

  private assigneeRequestSequence = 0;

  ngOnInit(): void {
    void this.refresh();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
  }

  async refresh(): Promise<void> {
    const requestSequence = this.requestSequence + 1;

    this.requestSequence = requestSequence;
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const tickets = await this.service().list(
        this.createFilters(),
      );

      if (
        requestSequence === this.requestSequence
        && this.canManage()
      ) {
        await this.hydrateAssigneeNames(tickets);
      }

      if (requestSequence === this.requestSequence) {
        this.cacheAssignedUserNames(tickets);
        this.tickets.set(tickets);
      }
    } catch {
      if (requestSequence === this.requestSequence) {
        this.errorMessage.set(
          'Não foi possível carregar os chamados.',
        );
      }
    } finally {
      if (requestSequence === this.requestSequence) {
        this.loading.set(false);
      }
    }
  }

  onSearchTermChange(
    value: string,
  ): void {
    this.searchTerm.set(value);

    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }

    this.searchTimer = setTimeout(() => {
      this.searchTimer = null;
      void this.refresh();
    }, 300);
  }

  onClientFilterChange(
    value: string,
  ): void {
    this.clientFilter.set(value);
    void this.refresh();
  }

  onStatusFilterChange(
    value: TicketStatusFilter,
  ): void {
    this.statusFilter.set(value);
    void this.refresh();
  }

  onPriorityFilterChange(
    value: TicketPriorityFilter,
  ): void {
    this.priorityFilter.set(value);
    void this.refresh();
  }

  openCreate(): void {
    if (!this.canManage()) {
      return;
    }

    const firstClient = this.clients().find(
      client => client.active,
    );

    if (!firstClient) {
      this.operationError.set(
        'Cadastre ou ative um cliente antes de abrir um chamado.',
      );
      return;
    }

    this.selectedTicket.set(null);
    this.draft.set({
      ...EMPTY_DRAFT,
      clientId: firstClient.id,
    });
    this.operationError.set(null);
    this.operationMessage.set(null);
    this.formVisible.set(true);

    void this.loadAssignees(firstClient.id);
    this.scrollToForm();
  }

  openEdit(
    ticket: Ticket,
  ): void {
    if (!this.canManage()) {
      return;
    }

    this.selectedTicket.set(ticket);
    this.draft.set({
      clientId: ticket.clientId,
      title: ticket.title,
      description: ticket.description,
      priority: ticket.priority,
      assignedToUserId: ticket.assignedToUserId,
    });
    this.operationError.set(null);
    this.operationMessage.set(null);
    this.formVisible.set(true);

    void this.loadAssignees(ticket.clientId);
    this.scrollToForm();
  }

  closeForm(): void {
    if (this.saving()) {
      return;
    }

    this.selectedTicket.set(null);
    this.draft.set(EMPTY_DRAFT);
    this.assignees.set([]);
    this.formVisible.set(false);
    this.operationError.set(null);
  }

  onDraftClientChange(
    clientId: string,
  ): void {
    this.updateDraft({
      clientId,
      assignedToUserId: null,
    });

    void this.loadAssignees(clientId);
  }

  onDraftTitleChange(
    title: string,
  ): void {
    this.updateDraft({ title });
  }

  onDraftDescriptionChange(
    description: string,
  ): void {
    this.updateDraft({ description });
  }

  onDraftPriorityChange(
    priority: TicketPriority,
  ): void {
    this.updateDraft({ priority });
  }

  onDraftAssigneeChange(
    assignedToUserId: string,
  ): void {
    this.updateDraft({
      assignedToUserId: assignedToUserId || null,
    });
  }

  async saveTicket(): Promise<void> {
    if (!this.canManage() || this.saving()) {
      return;
    }

    const draft = this.draft();
    const client = this.findClient(draft.clientId);

    if (!client) {
      this.operationError.set(
        'Selecione um cliente válido.',
      );
      return;
    }

    this.saving.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      const selectedTicket = this.selectedTicket();

      if (selectedTicket) {
        const input: TicketUpdateInput = {
          title: draft.title,
          description: draft.description,
          priority: draft.priority,
          assignedToUserId: draft.assignedToUserId,
        };

        await this.service().update(
          selectedTicket.id,
          input,
        );

        this.operationMessage.set(
          'Chamado atualizado com sucesso.',
        );
      } else {
        const input: TicketCreateInput = {
          environmentId: client.environmentId,
          clientId: client.id,
          title: draft.title,
          description: draft.description,
          priority: draft.priority,
          assignedToUserId: draft.assignedToUserId,
        };

        await this.service().create(input);

        this.operationMessage.set(
          'Chamado aberto com sucesso.',
        );
      }

      this.selectedTicket.set(null);
      this.draft.set(EMPTY_DRAFT);
      this.assignees.set([]);
      this.formVisible.set(false);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async changeStatus(
    ticket: Ticket,
    status: TicketStatus,
  ): Promise<void> {
    if (
      !this.canManage()
      || this.changingStatusTicketId()
      || status === ticket.status
    ) {
      return;
    }

    if (!STATUS_TRANSITIONS[ticket.status].includes(status)) {
      this.operationError.set(
        'A transição de status selecionada não é permitida.',
      );
      return;
    }

    this.changingStatusTicketId.set(ticket.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service().updateStatus(
        ticket.id,
        { status },
      );

      this.operationMessage.set(
        status === 'closed'
          ? 'Chamado encerrado com sucesso.'
          : status === 'open' && ticket.status === 'closed'
            ? 'Chamado reaberto com sucesso.'
            : 'Status atualizado com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.changingStatusTicketId.set(null);
    }
  }

  activeClients(): readonly Client[] {
    return this.clients().filter(client => client.active);
  }

  clientName(
    clientId: string,
  ): string {
    const client = this.findClient(clientId);

    return client?.fantasyName
      || client?.companyName
      || 'Cliente não identificado';
  }

  assigneeName(
    userId: string | null,
  ): string {
    if (!userId) {
      return 'Não atribuído';
    }

    return this.assigneeNames.get(userId)
      ?? `Usuário ${userId.slice(0, 8)}`;
  }

  statusLabel(
    status: TicketStatus,
  ): string {
    const labels: Record<TicketStatus, string> = {
      open: 'Aberto',
      in_progress: 'Em andamento',
      pending: 'Pendente',
      closed: 'Encerrado',
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

  statusOptions(
    ticket: Ticket,
  ): readonly TicketStatus[] {
    return [
      ticket.status,
      ...STATUS_TRANSITIONS[ticket.status],
    ];
  }

  formatDate(
    value: string | null,
  ): string {
    if (!value) {
      return '—';
    }

    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(new Date(value));
  }

  openDetails(
    ticket: Ticket,
  ): void {
    this.detailsTicketId.set(
      ticket.id,
    );
  }

  closeDetails(): void {
    this.detailsTicketId.set(null);
  }

  private createFilters(): TicketFilters {
    const search = this.searchTerm().trim();
    const clientId = this.clientFilter();
    const status = this.statusFilter();
    const priority = this.priorityFilter();

    return {
      clientId: clientId === 'all'
        ? undefined
        : clientId,
      status: status === 'all'
        ? undefined
        : status,
      priority: priority === 'all'
        ? undefined
        : priority,
      search: search || undefined,
    };
  }

  private updateDraft(
    changes: Partial<TicketDraft>,
  ): void {
    this.draft.update(draft => ({
      ...draft,
      ...changes,
    }));
  }

  private findClient(
    clientId: string,
  ): Client | undefined {
    return this.clients().find(
      client => client.id === clientId,
    );
  }

  private async loadAssignees(
    clientId: string,
  ): Promise<void> {
    const requestSequence = this.assigneeRequestSequence + 1;

    this.assigneeRequestSequence = requestSequence;
    this.loadingAssignees.set(true);

    try {
      const assignees = await this.getAssignees(clientId);

      if (requestSequence === this.assigneeRequestSequence) {
        this.assignees.set(assignees);
      }
    } catch {
      if (requestSequence === this.assigneeRequestSequence) {
        this.assignees.set([]);
        this.operationError.set(
          'Não foi possível carregar os responsáveis.',
        );
      }
    } finally {
      if (requestSequence === this.assigneeRequestSequence) {
        this.loadingAssignees.set(false);
      }
    }
  }

  private async hydrateAssigneeNames(
    tickets: readonly Ticket[],
  ): Promise<void> {
    const clientIds = [
      ...new Set(
        tickets
          .filter(ticket => ticket.assignedToUserId)
          .map(ticket => ticket.clientId),
      ),
    ];

    await Promise.allSettled(
      clientIds.map(clientId => this.getAssignees(clientId)),
    );
  }

  private cacheAssignedUserNames(
    tickets: readonly Ticket[],
  ): void {
    for (const ticket of tickets) {
      if (
        ticket.assignedToUserId
        && ticket.assignedToUserName
      ) {
        this.assigneeNames.set(
          ticket.assignedToUserId,
          ticket.assignedToUserName,
        );
      }
    }
  }

  private async getAssignees(
    clientId: string,
  ): Promise<readonly TicketAssignee[]> {
    const cached = this.assigneesByClient.get(clientId);

    if (cached) {
      return cached;
    }

    const assignees = await this.assigneeService().list(clientId);

    this.assigneesByClient.set(clientId, assignees);

    for (const assignee of assignees) {
      this.assigneeNames.set(
        assignee.id,
        assignee.name,
      );
    }

    return assignees;
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível concluir a operação.';
    }

    if (error.status === 0) {
      return 'Não foi possível acessar a API.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O chamado, Cliente ou responsável não foi encontrado.';
    }

    if (error.status === 409) {
      return 'A operação conflita com o estado atual do chamado.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

  private scrollToForm(): void {
    setTimeout(() => {
      document.querySelector(
        '.tickets__form',
      )?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    });
  }

}
