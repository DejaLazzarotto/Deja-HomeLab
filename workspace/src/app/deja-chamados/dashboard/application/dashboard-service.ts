/*
 * Deja Chamados
 *
 * Dashboard Application
 *
 * Consolida os dados de clientes, chamados e histórico
 * para produzir os indicadores operacionais e gerenciais.
 */

import {
  Client,
} from '../../clients';

import {
  Ticket,
  TicketTimelineEvent,
  TICKET_PRIORITY_LABELS,
  TICKET_STATUS_LABELS,
  calculateTicketSla,
} from '../../tickets';

import {
  DashboardAverageResolutionTime,
  DashboardBacklog,
  DashboardData,
  DashboardManagerData,
  DashboardManagerMetricData,
  DashboardMttr,
  DashboardOldestTicket,
  DashboardPriorityBacklog,
  DashboardResponsibleBacklog,
  DashboardResponsibleMttr,
  DashboardResponsibleRanking,
  DashboardSlaChartItem,
  DashboardSlaData,
  DashboardSlaMonthlyTrend,
  DashboardTopClient,
} from '../domain';

export interface DashboardSourceData {
  clients: readonly Client[];
  tickets: readonly Ticket[];
  timelineByTicketId: ReadonlyMap<
    string,
    readonly TicketTimelineEvent[]
  >;
}

export class DashboardService {

  buildDashboardData(
    source: DashboardSourceData,
  ): DashboardData {
    const clients = [...source.clients];
    const tickets = [...source.tickets];

    const openSlaTickets = this.getOpenTickets(tickets);

    const withinSla =
      this.countTicketsWithinSla(openSlaTickets);

    const nearExpiration =
      this.countTicketsNearExpiration(openSlaTickets);

    const expiredSla =
      this.countTicketsExpiredSla(openSlaTickets);

    const slaComplied =
      this.calculateSlaCompliedPercentage(tickets);

    const slaViolated =
      this.calculateSlaViolatedPercentage(tickets);

    return {
      summary: [
        {
          title: 'Clientes Ativos',
          value: clients.filter(
            (client) => client.active,
          ).length,
          icon: 'groups',
          description: 'Clientes habilitados',
        },
        {
          title: 'Total de Chamados',
          value: tickets.length,
          icon: 'confirmation_number',
          description: 'Chamados registrados',
        },
        {
          title: 'Chamados Abertos',
          value: this.countTicketsByStatus(
            tickets,
            'open',
          ),
          icon: 'mark_unread_chat_alt',
          description: 'Aguardando atendimento',
        },
        {
          title: 'Em Atendimento',
          value: this.countTicketsByStatus(
            tickets,
            'in_progress',
          ),
          icon: 'support_agent',
          description: 'Em execução',
        },
        {
          title: 'Pendentes',
          value: this.countTicketsByStatus(
            tickets,
            'pending',
          ),
          icon: 'pending_actions',
          description: 'Aguardando retorno',
        },
        {
          title: 'Encerrados',
          value: this.countTicketsByStatus(
            tickets,
            'closed',
          ),
          icon: 'task_alt',
          description: 'Chamados finalizados',
        },
        {
          title: 'Alta Prioridade',
          value: tickets.filter(
            (ticket) => ticket.priority === 'high',
          ).length,
          icon: 'priority_high',
          description: 'Chamados importantes',
        },
        {
          title: 'Críticos',
          value: tickets.filter(
            (ticket) => ticket.priority === 'critical',
          ).length,
          icon: 'report',
          description: 'Exigem ação imediata',
        },
        {
          title: 'Dentro do Prazo',
          value: withinSla,
          icon: 'verified',
          description: 'Chamados dentro do prazo previsto',
        },
        {
          title: 'Próximos do Prazo',
          value: nearExpiration,
          icon: 'schedule',
          description: 'Chamados próximos do vencimento',
        },
        {
          title: 'Prazo Vencido',
          value: expiredSla,
          icon: 'warning',
          description: 'Chamados com prazo excedido',
        },
        {
          title: 'Atendidos no Prazo',
          value: slaComplied,
          icon: 'trending_up',
          description: 'Chamados encerrados dentro do prazo',
          suffix: '%',
        },
        {
          title: 'Atendidos Fora do Prazo',
          value: slaViolated,
          icon: 'trending_down',
          description: 'Chamados encerrados fora do prazo',
          suffix: '%',
        },
      ],
      latestTickets: this.getLatestTickets(
        tickets,
        clients,
      ),
    };
  }

  buildSlaData(
    source: DashboardSourceData,
  ): DashboardSlaData {
    const tickets = [...source.tickets];

    return {
      byPriority: this.getSlaByPriority(tickets),
      byResponsible: this.getSlaByResponsible(tickets),
      monthlyTrend: this.getMonthlyTrend(tickets),
    };
  }

  buildManagerData(
    source: DashboardSourceData,
  ): DashboardManagerData {
    const tickets = [...source.tickets];

    const averageResolutionTime =
      this.getAverageResolutionTime(tickets);

    const mttr = this.getMttr(
      tickets,
      source.timelineByTicketId,
    );

    const responsibleMttr =
      this.getResponsibleMttr(
        tickets,
        source.timelineByTicketId,
      );

    const responsibleMetrics =
      this.getResponsibleMetrics(
        responsibleMttr,
      );

    const reopenRate =
      this.getReopenRate(
        tickets,
        source.timelineByTicketId,
      );

    const responsibleReopenRate =
      this.getResponsibleReopenRate(
        tickets,
        source.timelineByTicketId,
      );

    const reopenMetrics =
      this.getReopenMetrics(
        responsibleReopenRate,
      );

    const backlog =
      this.getBacklog(tickets);

    const responsibleBacklog =
      this.getResponsibleBacklog(tickets);

    const backlogMetrics =
      this.getBacklogMetrics(
        responsibleBacklog,
      );

    const priorityBacklog =
      this.getPriorityBacklog(tickets);

    const priorityBacklogMetrics =
      this.getPriorityBacklogMetrics(
        priorityBacklog,
      );

    const responsibleRanking =
      this.getResponsibleRanking(
        responsibleBacklog,
        responsibleMttr,
        responsibleReopenRate,
      );

    const resolutionRate =
      this.getResolutionRate(tickets);

    return {
      topClients: this.getTopClients(
        tickets,
        [...source.clients],
      ),
      oldestOpenTickets:
        this.getOldestOpenTickets(
          tickets,
          [...source.clients],
        ),
      averageResolutionTime,
      mttr,
      responsibleMttr,
      responsibleMetrics,
      reopenRate,
      responsibleReopenRate,
      reopenMetrics,
      backlog,
      responsibleBacklog,
      backlogMetrics,
      priorityBacklog,
      responsibleRanking,
      priorityBacklogMetrics,
      metrics: this.getManagerMetrics(
        averageResolutionTime,
        mttr,
        resolutionRate,
        reopenRate,
        backlog,
      ),
    };
  }

  private getBacklog(
    tickets: Ticket[],
  ): DashboardBacklog {
    return {
      totalTickets:
        this.getOpenTickets(tickets).length,
    };
  }

  private getResponsibleBacklog(
    tickets: Ticket[],
  ): DashboardResponsibleBacklog[] {
    const groups =
      new Map<string, Ticket[]>();

    this.getOpenTickets(tickets)
      .forEach((ticket) => {
        const assignedTo =
          this.getTicketResponsible(ticket);

        const current =
          groups.get(assignedTo) ?? [];

        current.push(ticket);
        groups.set(assignedTo, current);
      });

    return Array.from(groups.entries())
      .map(([assignedTo, items]) => ({
        assignedTo,
        totalTickets: items.length,
      }))
      .sort(
        (a, b) =>
          b.totalTickets - a.totalTickets,
      );
  }

  private getPriorityBacklog(
    tickets: Ticket[],
  ): DashboardPriorityBacklog[] {
    const groups =
      new Map<string, number>();

    this.getOpenTickets(tickets)
      .forEach((ticket) => {
        groups.set(
          ticket.priority,
          (groups.get(ticket.priority) ?? 0) + 1,
        );
      });

    return Array.from(groups.entries())
      .map(([priority, totalTickets]) => ({
        priority,
        totalTickets,
      }))
      .sort(
        (a, b) =>
          b.totalTickets - a.totalTickets,
      );
  }

  private getBacklogMetrics(
    backlog: DashboardResponsibleBacklog[],
  ): DashboardManagerMetricData[] {
    return backlog.map((item) => ({
      title: item.assignedTo,
      value: String(item.totalTickets),
      description: 'Chamado(s) não encerrado(s)',
      icon: 'inventory_2',
    }));
  }

  private getPriorityBacklogMetrics(
    backlog: DashboardPriorityBacklog[],
  ): DashboardManagerMetricData[] {
    return backlog.map((item) => ({
      title:
        TICKET_PRIORITY_LABELS[
          item.priority as keyof typeof TICKET_PRIORITY_LABELS
        ],
      value: String(item.totalTickets),
      description: 'Chamado(s) não encerrado(s)',
      icon: 'flag',
    }));
  }

  private getResponsibleRanking(
    responsibleBacklog:
      DashboardResponsibleBacklog[],
    responsibleMttr:
      DashboardResponsibleMttr[],
    responsibleReopenRate: {
      assignedTo: string;
      reopenedTickets: number;
      totalClosedTickets: number;
      percentage: number;
    }[],
  ): DashboardResponsibleRanking[] {
    return responsibleBacklog.map(
      (backlog) => {
        const mttr =
          responsibleMttr.find(
            (item) =>
              item.assignedTo ===
              backlog.assignedTo,
          );

        const reopen =
          responsibleReopenRate.find(
            (item) =>
              item.assignedTo ===
              backlog.assignedTo,
          );

        return {
          assignedTo: backlog.assignedTo,
          backlog: backlog.totalTickets,
          mttr: mttr?.formattedValue ?? '0h',
          reopenRate:
            reopen?.percentage ?? 0,
        };
      },
    );
  }

  private getManagerMetrics(
    averageResolutionTime:
      DashboardAverageResolutionTime,
    mttr: DashboardMttr,
    resolutionRate: number,
    reopenRate: {
      reopenedTickets: number;
      totalClosedTickets: number;
      percentage: number;
    },
    backlog: DashboardBacklog,
  ): DashboardManagerMetricData[] {
    return [
      {
        title: 'Tempo médio de atendimento',
        value:
          averageResolutionTime.formattedValue,
        description:
          `${averageResolutionTime.totalClosedTickets} chamado(s) encerrado(s)`,
        icon: 'schedule',
      },
      {
        title: 'Tempo médio de solução',
        value: mttr.formattedValue,
        description:
          `${mttr.totalClosedTickets} chamado(s) encerrado(s)`,
        icon: 'build_circle',
      },
      {
        title: 'Taxa de resolução',
        value: `${resolutionRate}%`,
        description:
          'Chamados encerrados sobre o total registrado',
        icon: 'task_alt',
      },
      {
        title: 'Taxa de reabertura',
        value: `${reopenRate.percentage}%`,
        description:
          `${reopenRate.reopenedTickets} chamado(s) reaberto(s) de ${reopenRate.totalClosedTickets} encerrado(s)`,
        icon: 'restart_alt',
      },
      {
        title: 'Backlog atual',
        value: String(backlog.totalTickets),
        description: 'Chamados não encerrados',
        icon: 'inventory_2',
      },
    ];
  }

  private getResponsibleMetrics(
    items: DashboardResponsibleMttr[],
  ): DashboardManagerMetricData[] {
    return items.map((item) => ({
      title: item.assignedTo,
      value: item.formattedValue,
      description:
        `${item.totalClosedTickets} chamado(s) encerrado(s)`,
      icon: 'person',
    }));
  }

  private getReopenMetrics(
    items: {
      assignedTo: string;
      reopenedTickets: number;
      totalClosedTickets: number;
      percentage: number;
    }[],
  ): DashboardManagerMetricData[] {
    return items.map((item) => ({
      title: item.assignedTo,
      value: `${item.percentage}%`,
      description:
        `${item.reopenedTickets} reaberto(s) de ${item.totalClosedTickets} encerrado(s)`,
      icon: 'restart_alt',
    }));
  }

  private getReopenRate(
    tickets: Ticket[],
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ) {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    if (closed.length === 0) {
      return {
        reopenedTickets: 0,
        totalClosedTickets: 0,
        percentage: 0,
      };
    }

    const reopenedTickets =
      closed.filter((ticket) =>
        this.wasTicketReopened(
          ticket,
          timelineByTicketId,
        ),
      ).length;

    return {
      reopenedTickets,
      totalClosedTickets: closed.length,
      percentage: Math.round(
        (reopenedTickets / closed.length) * 100,
      ),
    };
  }

  private getResponsibleReopenRate(
    tickets: Ticket[],
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ) {
    const groups =
      new Map<string, Ticket[]>();

    this.getClosedTicketsWithClosedAt(tickets)
      .forEach((ticket) => {
        const assignedTo =
          this.getTicketResponsible(ticket);

        const current =
          groups.get(assignedTo) ?? [];

        current.push(ticket);
        groups.set(assignedTo, current);
      });

    return Array.from(groups.entries())
      .map(([assignedTo, items]) => {
        const reopenedTickets =
          items.filter((ticket) =>
            this.wasTicketReopened(
              ticket,
              timelineByTicketId,
            ),
          ).length;

        return {
          assignedTo,
          reopenedTickets,
          totalClosedTickets: items.length,
          percentage: Math.round(
            (reopenedTickets / items.length) * 100,
          ),
        };
      })
      .sort(
        (a, b) =>
          a.percentage - b.percentage,
      );
  }

  private wasTicketReopened(
    ticket: Ticket,
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ): boolean {
    return (
      timelineByTicketId.get(ticket.id) ?? []
    ).some(
      (event) =>
        event.eventType === 'status_changed' &&
        event.previousValue === 'closed' &&
        event.newValue !== 'closed',
    );
  }

  private getTopClients(
    tickets: Ticket[],
    clients: Client[],
  ): DashboardTopClient[] {
    return clients
      .map((client) => ({
        clientId: client.id,
        clientName:
          client.fantasyName ||
          client.companyName,
        totalTickets:
          tickets.filter(
            (ticket) =>
              ticket.clientId === client.id,
          ).length,
      }))
      .filter(
        (client) =>
          client.totalTickets > 0,
      )
      .sort(
        (a, b) =>
          b.totalTickets - a.totalTickets,
      )
      .slice(0, 5);
  }

  private getOldestOpenTickets(
    tickets: Ticket[],
    clients: Client[],
  ): DashboardOldestTicket[] {
    const now = Date.now();

    return this.getOpenTickets(tickets)
      .sort(
        (a, b) =>
          new Date(a.createdAt).getTime() -
          new Date(b.createdAt).getTime(),
      )
      .slice(0, 5)
      .map((ticket) => {
        const createdAt =
          new Date(ticket.createdAt);

        return {
          ticketId: ticket.id,
          title: ticket.title,
          clientName:
            this.getClientName(
              ticket.clientId,
              clients,
            ),
          createdAt: ticket.createdAt,
          daysOpen: Math.floor(
            (now - createdAt.getTime()) /
              (1000 * 60 * 60 * 24),
          ),
        };
      });
  }

  private getAverageResolutionTime(
    tickets: Ticket[],
  ): DashboardAverageResolutionTime {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    if (closed.length === 0) {
      return {
        totalClosedTickets: 0,
        averageHours: 0,
        averageDays: 0,
        formattedValue: '0h',
      };
    }

    const totalHours =
      this.calculateTotalResolutionHours(closed);

    const averageHours =
      totalHours / closed.length;

    return {
      totalClosedTickets: closed.length,
      averageHours:
        Number(averageHours.toFixed(2)),
      averageDays:
        Number((averageHours / 24).toFixed(2)),
      formattedValue:
        this.formatAverageResolutionTime(
          averageHours,
        ),
    };
  }

  private getMttr(
    tickets: Ticket[],
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ): DashboardMttr {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    if (closed.length === 0) {
      return {
        totalClosedTickets: 0,
        averageHours: 0,
        averageDays: 0,
        formattedValue: '0h',
      };
    }

    const totalHours =
      closed.reduce((total, ticket) => {
        const startedAt =
          this.getTicketStartedAt(
            ticket,
            timelineByTicketId,
          );

        const closedAt =
          new Date(ticket.closedAt!).getTime();

        return total +
          (closedAt - startedAt) /
          (1000 * 60 * 60);
      }, 0);

    const averageHours =
      totalHours / closed.length;

    return {
      totalClosedTickets: closed.length,
      averageHours:
        Number(averageHours.toFixed(2)),
      averageDays:
        Number((averageHours / 24).toFixed(2)),
      formattedValue:
        this.formatAverageResolutionTime(
          averageHours,
        ),
    };
  }

  private getResponsibleMttr(
    tickets: Ticket[],
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ): DashboardResponsibleMttr[] {
    const groups =
      new Map<string, Ticket[]>();

    this.getClosedTicketsWithClosedAt(tickets)
      .forEach((ticket) => {
        const assignedTo =
          this.getTicketResponsible(ticket);

        const current =
          groups.get(assignedTo) ?? [];

        current.push(ticket);
        groups.set(assignedTo, current);
      });

    return Array.from(groups.entries())
      .map(([assignedTo, items]) => {
        const totalHours =
          items.reduce((total, ticket) => {
            const startedAt =
              this.getTicketStartedAt(
                ticket,
                timelineByTicketId,
              );

            const closedAt =
              new Date(ticket.closedAt!).getTime();

            return total +
              (closedAt - startedAt) /
              (1000 * 60 * 60);
          }, 0);

        const averageHours =
          totalHours / items.length;

        return {
          assignedTo,
          totalClosedTickets: items.length,
          averageHours:
            Number(averageHours.toFixed(2)),
          averageDays:
            Number(
              (averageHours / 24).toFixed(2),
            ),
          formattedValue:
            this.formatAverageResolutionTime(
              averageHours,
            ),
        };
      })
      .sort(
        (a, b) =>
          a.averageHours - b.averageHours,
      );
  }

  private getResolutionRate(
    tickets: Ticket[],
  ): number {
    if (tickets.length === 0) {
      return 0;
    }

    const closed =
      tickets.filter(
        (ticket) =>
          ticket.status === 'closed',
      ).length;

    return Math.round(
      (closed / tickets.length) * 100,
    );
  }

  private getTicketStartedAt(
    ticket: Ticket,
    timelineByTicketId:
      DashboardSourceData['timelineByTicketId'],
  ): number {
    const startedEvent =
      [
        ...(timelineByTicketId.get(ticket.id) ?? []),
      ]
        .filter(
          (event) =>
            event.eventType === 'status_changed' &&
            event.newValue === 'in_progress',
        )
        .sort(
          (a, b) =>
            new Date(a.createdAt).getTime() -
            new Date(b.createdAt).getTime(),
        )[0];

    if (startedEvent) {
      return new Date(
        startedEvent.createdAt,
      ).getTime();
    }

    if (ticket.status === 'in_progress') {
      return new Date(
        ticket.updatedAt,
      ).getTime();
    }

    return new Date(
      ticket.createdAt,
    ).getTime();
  }

  private calculateTotalResolutionHours(
    tickets: Ticket[],
  ): number {
    return tickets.reduce(
      (total, ticket) => {
        const createdAt =
          new Date(ticket.createdAt).getTime();

        const closedAt =
          new Date(ticket.closedAt!).getTime();

        return total +
          (closedAt - createdAt) /
          (1000 * 60 * 60);
      },
      0,
    );
  }

  private countTicketsByStatus(
    tickets: Ticket[],
    status: Ticket['status'],
  ): number {
    return tickets.filter(
      (ticket) =>
        ticket.status === status,
    ).length;
  }

  private countTicketsWithinSla(
    tickets: Ticket[],
  ): number {
    return tickets.filter(
      (ticket) =>
        !calculateTicketSla(ticket).isExpired,
    ).length;
  }

  private countTicketsNearExpiration(
    tickets: Ticket[],
  ): number {
    return tickets.filter((ticket) => {
      const sla =
        calculateTicketSla(ticket);

      return (
        !sla.isExpired &&
        sla.remainingHours > 0 &&
        sla.remainingHours <= 8
      );
    }).length;
  }

  private countTicketsExpiredSla(
    tickets: Ticket[],
  ): number {
    return tickets.filter(
      (ticket) =>
        calculateTicketSla(ticket).isExpired,
    ).length;
  }

  private calculateSlaCompliedPercentage(
    tickets: Ticket[],
  ): number {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    if (closed.length === 0) {
      return 0;
    }

    const complied =
      closed.filter(
        (ticket) =>
          this.wasTicketClosedWithinSla(ticket),
      ).length;

    return Math.round(
      (complied / closed.length) * 100,
    );
  }

  private calculateSlaViolatedPercentage(
    tickets: Ticket[],
  ): number {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    if (closed.length === 0) {
      return 0;
    }

    const violated =
      closed.filter(
        (ticket) =>
          !this.wasTicketClosedWithinSla(ticket),
      ).length;

    return Math.round(
      (violated / closed.length) * 100,
    );
  }

  private getClosedTicketsWithClosedAt(
    tickets: Ticket[],
  ): Ticket[] {
    return tickets.filter(
      (ticket) =>
        ticket.status === 'closed' &&
        !!ticket.closedAt,
    );
  }

  private getOpenTickets(
    tickets: Ticket[],
  ): Ticket[] {
    return tickets.filter(
      (ticket) =>
        ticket.status !== 'closed',
    );
  }

  private wasTicketClosedWithinSla(
    ticket: Ticket,
  ): boolean {
    if (!ticket.closedAt) {
      return false;
    }

    const sla =
      calculateTicketSla(ticket);

    return (
      new Date(ticket.closedAt).getTime() <=
      new Date(sla.dueAt).getTime()
    );
  }

  private getSlaByPriority(
    tickets: Ticket[],
  ): DashboardSlaChartItem[] {
    return Object.entries(
      TICKET_PRIORITY_LABELS,
    ).map(([priority, label]) => {
      const filtered =
        tickets.filter(
          (ticket) =>
            ticket.priority === priority,
        );

      return this.buildSlaChartItem(
        label,
        filtered,
      );
    });
  }

  private getSlaByResponsible(
    tickets: Ticket[],
  ): DashboardSlaChartItem[] {
    const responsibleNames =
      Array.from(
        new Set(
          tickets.map(
            (ticket) =>
              this.getTicketResponsible(ticket),
          ),
        ),
      ).sort(
        (a, b) =>
          a.localeCompare(b),
      );

    return responsibleNames.map(
      (responsible) => {
        const filtered =
          tickets.filter(
            (ticket) =>
              this.getTicketResponsible(ticket) ===
              responsible,
          );

        return this.buildSlaChartItem(
          responsible,
          filtered,
        );
      },
    );
  }

  private getMonthlyTrend(
    tickets: Ticket[],
  ): DashboardSlaMonthlyTrend[] {
    const months =
      new Map<
        string,
        DashboardSlaMonthlyTrend
      >();

    tickets.forEach((ticket) => {
      const openedMonth =
        this.getMonthKey(ticket.createdAt);

      const openedTrend =
        this.getOrCreateMonthlyTrend(
          months,
          openedMonth,
        );

      openedTrend.opened += 1;

      if (
        ticket.status !== 'closed' ||
        !ticket.closedAt
      ) {
        return;
      }

      const closedMonth =
        this.getMonthKey(ticket.closedAt);

      const closedTrend =
        this.getOrCreateMonthlyTrend(
          months,
          closedMonth,
        );

      closedTrend.closed += 1;

      if (
        this.wasTicketClosedWithinSla(ticket)
      ) {
        closedTrend.complied += 1;
      } else {
        closedTrend.violated += 1;
      }
    });

    return Array.from(
      months.values(),
    ).sort(
      (a, b) =>
        a.month.localeCompare(b.month),
    );
  }

  private getOrCreateMonthlyTrend(
    months: Map<
      string,
      DashboardSlaMonthlyTrend
    >,
    month: string,
  ): DashboardSlaMonthlyTrend {
    const existing =
      months.get(month);

    if (existing) {
      return existing;
    }

    const created: DashboardSlaMonthlyTrend = {
      month,
      opened: 0,
      closed: 0,
      complied: 0,
      violated: 0,
    };

    months.set(month, created);

    return created;
  }

  private buildSlaChartItem(
    label: string,
    tickets: Ticket[],
  ): DashboardSlaChartItem {
    const closed =
      this.getClosedTicketsWithClosedAt(tickets);

    const complied =
      closed.filter(
        (ticket) =>
          this.wasTicketClosedWithinSla(ticket),
      ).length;

    const violated =
      closed.length - complied;

    const open =
      this.getOpenTickets(tickets);

    return {
      label,
      total: tickets.length,
      withinSla:
        this.countTicketsWithinSla(open),
      expiredSla:
        this.countTicketsExpiredSla(open),
      complied,
      violated,
      compliedPercentage:
        this.calculatePercentage(
          complied,
          closed.length,
        ),
      violatedPercentage:
        this.calculatePercentage(
          violated,
          closed.length,
        ),
    };
  }

  private calculatePercentage(
    value: number,
    total: number,
  ): number {
    if (total === 0) {
      return 0;
    }

    return Math.round(
      (value / total) * 100,
    );
  }

  private getTicketResponsible(
    ticket: Ticket,
  ): string {
    return (
      ticket.assignedToUserName ??
      'Sem responsável'
    );
  }

  private getMonthKey(
    value: string,
  ): string {
    const date =
      new Date(value);

    const year =
      date.getFullYear();

    const month =
      String(
        date.getMonth() + 1,
      ).padStart(2, '0');

    return `${year}-${month}`;
  }

  private formatAverageResolutionTime(
    averageHours: number,
  ): string {
    if (averageHours < 24) {
      return `${averageHours.toFixed(1)} h`;
    }

    return `${(averageHours / 24).toFixed(1)} dias`;
  }

  private getLatestTickets(
    tickets: Ticket[],
    clients: Client[],
  ) {
    return [...tickets]
      .sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() -
          new Date(a.updatedAt).getTime(),
      )
      .slice(0, 5)
      .map((ticket) => ({
        id: ticket.id,
        title: ticket.title,
        clientName:
          this.getClientName(
            ticket.clientId,
            clients,
          ),
        status:
          TICKET_STATUS_LABELS[
            ticket.status
          ],
        priority:
          TICKET_PRIORITY_LABELS[
            ticket.priority
          ],
        updatedAt:
          this.formatUpdatedAt(
            ticket.updatedAt,
          ),
      }));
  }

  private getClientName(
    clientId: string,
    clients: Client[],
  ): string {
    const client =
      clients.find(
        (item) =>
          item.id === clientId,
      );

    return (
      client?.fantasyName ||
      client?.companyName ||
      'Cliente não encontrado'
    );
  }

  private formatUpdatedAt(
    value: string,
  ): string {
    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(
      new Date(value),
    );
  }

}