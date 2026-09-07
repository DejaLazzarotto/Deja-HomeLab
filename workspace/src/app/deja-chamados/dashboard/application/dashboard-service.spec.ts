import {
  Client,
} from '../../clients';

import {
  Ticket,
  TicketTimelineEvent,
} from '../../tickets';

import {
  DashboardService,
  DashboardSourceData,
} from './dashboard-service';

describe('DashboardService', () => {

  const service = new DashboardService();

  const clients: Client[] = [
    {
      id: 'client-1',
      organizationId: 'org-1',
      tenantId: 'tenant-1',
      environmentId: 'environment-1',
      companyName: 'Empresa Um Ltda',
      fantasyName: 'Empresa Um',
      document: '12345678000100',
      contactName: 'Contato',
      phone: '',
      whatsapp: '',
      email: 'empresa@teste.com',
      city: 'Caxias do Sul',
      state: 'RS',
      notes: '',
      active: true,
      createdAt: '2026-09-01T08:00:00',
      updatedAt: '2026-09-01T08:00:00',
      totalTickets: 2,
    },
  ];

  const tickets: Ticket[] = [
    {
      id: 'ticket-open',
      organizationId: 'org-1',
      tenantId: 'tenant-1',
      environmentId: 'environment-1',
      clientId: 'client-1',
      title: 'Chamado aberto',
      description: 'Descrição',
      status: 'open',
      priority: 'medium',
      openedByUserId: 'user-1',
      assignedToUserId: 'user-2',
      assignedToUserName: 'Analista',
      closedByUserId: null,
      closedAt: null,
      createdAt: '2026-09-07T10:00:00',
      updatedAt: '2026-09-07T10:00:00',
    },
    {
      id: 'ticket-closed',
      organizationId: 'org-1',
      tenantId: 'tenant-1',
      environmentId: 'environment-1',
      clientId: 'client-1',
      title: 'Chamado encerrado',
      description: 'Descrição',
      status: 'closed',
      priority: 'high',
      openedByUserId: 'user-1',
      assignedToUserId: 'user-2',
      assignedToUserName: 'Analista',
      closedByUserId: 'user-2',
      closedAt: '2026-09-06T14:00:00',
      createdAt: '2026-09-05T08:00:00',
      updatedAt: '2026-09-06T14:00:00',
    },
  ];

  const timeline: TicketTimelineEvent[] = [
    {
      id: 'event-1',
      ticketId: 'ticket-closed',
      eventType: 'status_changed',
      description: 'Status alterado.',
      previousValue: 'open',
      newValue: 'in_progress',
      createdByUserId: 'user-2',
      createdAt: '2026-09-05T10:00:00',
    },
    {
      id: 'event-2',
      ticketId: 'ticket-closed',
      eventType: 'status_changed',
      description: 'Status alterado.',
      previousValue: 'closed',
      newValue: 'open',
      createdByUserId: 'user-2',
      createdAt: '2026-09-05T15:00:00',
    },
    {
      id: 'event-3',
      ticketId: 'ticket-closed',
      eventType: 'status_changed',
      description: 'Status alterado.',
      previousValue: 'open',
      newValue: 'closed',
      createdByUserId: 'user-2',
      createdAt: '2026-09-06T14:00:00',
    },
  ];

  const source: DashboardSourceData = {
    clients,
    tickets,
    timelineByTicketId: new Map([
      [
        'ticket-closed',
        timeline,
      ],
    ]),
  };

  it('gera o resumo operacional', () => {
    const data = service.buildDashboardData(
      source,
    );

    expect(
      data.summary.find(
        (item) =>
          item.title === 'Clientes Ativos',
      )?.value,
    ).toBe(1);

    expect(
      data.summary.find(
        (item) =>
          item.title === 'Total de Chamados',
      )?.value,
    ).toBe(2);

    expect(
      data.summary.find(
        (item) =>
          item.title === 'Chamados Abertos',
      )?.value,
    ).toBe(1);

    expect(
      data.summary.find(
        (item) =>
          item.title === 'Encerrados',
      )?.value,
    ).toBe(1);

    expect(data.latestTickets.length).toBe(2);
    expect(
      data.latestTickets[0].id,
    ).toBe('ticket-open');
  });

  it('gera indicadores de SLA', () => {
    const data = service.buildSlaData(
      source,
    );

    expect(data.byPriority.length).toBe(4);

    const high = data.byPriority.find(
      (item) =>
        item.label === 'Alta',
    );

    expect(high?.total).toBe(1);
    expect(high?.violated).toBe(1);
  });

  it('usa a timeline para calcular MTTR', () => {
    const data = service.buildManagerData(
      source,
    );

    expect(
      data.mttr.totalClosedTickets,
    ).toBe(1);

    expect(
      data.mttr.averageHours,
    ).toBe(28);
  });

  it('detecta chamado reaberto pela timeline', () => {
    const data = service.buildManagerData(
      source,
    );

    expect(
      data.reopenRate.reopenedTickets,
    ).toBe(1);

    expect(
      data.reopenRate.totalClosedTickets,
    ).toBe(1);

    expect(
      data.reopenRate.percentage,
    ).toBe(100);
  });

  it('calcula backlog por responsável', () => {
    const data = service.buildManagerData(
      source,
    );

    expect(
      data.backlog.totalTickets,
    ).toBe(1);

    expect(
      data.responsibleBacklog,
    ).toEqual([
      {
        assignedTo: 'Analista',
        totalTickets: 1,
      },
    ]);
  });

});