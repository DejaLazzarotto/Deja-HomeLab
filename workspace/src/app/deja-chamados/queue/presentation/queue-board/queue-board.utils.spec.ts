import {
  describe,
  expect,
  it,
} from 'vitest';

import {
  Ticket,
} from '../../../tickets';

import {
  sortQueueTickets,
} from './queue-board.utils';

function ticket(
  overrides: Partial<Ticket>,
): Ticket {
  return {
    id: crypto.randomUUID(),
    organizationId: crypto.randomUUID(),
    tenantId: crypto.randomUUID(),
    environmentId: crypto.randomUUID(),
    clientId: crypto.randomUUID(),
    title: 'Chamado de teste',
    description: 'Descrição de teste',
    status: 'open',
    priority: 'medium',
    openedByUserId: crypto.randomUUID(),
    assignedToUserId: null,
    assignedToUserName: null,
    closedByUserId: null,
    closedAt: null,
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    ...overrides,
  };
}

describe('sortQueueTickets', () => {

  it('ordena chamados ativos por prioridade', () => {
    const tickets = [
      ticket({
        id: 'low',
        priority: 'low',
      }),
      ticket({
        id: 'critical',
        priority: 'critical',
      }),
      ticket({
        id: 'medium',
        priority: 'medium',
      }),
      ticket({
        id: 'high',
        priority: 'high',
      }),
    ];

    const result = sortQueueTickets(
      tickets,
      'open',
    );

    expect(
      result.map(item => item.id),
    ).toEqual([
      'critical',
      'high',
      'medium',
      'low',
    ]);
  });

  it('prioriza o chamado atualizado há mais tempo no empate de prioridade', () => {
    const tickets = [
      ticket({
        id: 'newer',
        priority: 'high',
        updatedAt: '2026-09-05T10:00:00.000Z',
      }),
      ticket({
        id: 'older',
        priority: 'high',
        updatedAt: '2026-09-02T10:00:00.000Z',
      }),
    ];

    const result = sortQueueTickets(
      tickets,
      'open',
    );

    expect(
      result.map(item => item.id),
    ).toEqual([
      'older',
      'newer',
    ]);
  });

  it('ordena chamados fechados pelo mais recentemente atualizado', () => {
    const tickets = [
      ticket({
        id: 'older',
        status: 'closed',
        updatedAt: '2026-09-02T10:00:00.000Z',
      }),
      ticket({
        id: 'newer',
        status: 'closed',
        updatedAt: '2026-09-05T10:00:00.000Z',
      }),
    ];

    const result = sortQueueTickets(
      tickets,
      'closed',
    );

    expect(
      result.map(item => item.id),
    ).toEqual([
      'newer',
      'older',
    ]);
  });

  it('retorna somente os chamados do status solicitado', () => {
    const tickets = [
      ticket({
        id: 'open',
        status: 'open',
      }),
      ticket({
        id: 'pending',
        status: 'pending',
      }),
    ];

    const result = sortQueueTickets(
      tickets,
      'pending',
    );

    expect(
      result.map(item => item.id),
    ).toEqual([
      'pending',
    ]);
  });

});
