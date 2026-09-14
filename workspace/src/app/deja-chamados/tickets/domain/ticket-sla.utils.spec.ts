import {
  Ticket,
} from './ticket';

import {
  calculateTicketSla,
  wasTicketClosedWithinSla,
} from './ticket-sla.utils';

describe('Ticket SLA utils', () => {

  const ticket: Ticket = {
    id: '11111111-1111-4111-8111-111111111111',
    organizationId: '22222222-2222-4222-8222-222222222222',
    tenantId: '33333333-3333-4333-8333-333333333333',
    environmentId: '44444444-4444-4444-8444-444444444444',
    clientId: '55555555-5555-4555-8555-555555555555',
    title: 'Falha no acesso',
    description: 'Usuário não consegue acessar.',
    status: 'open',
    priority: 'high',
    openedByUserId: '66666666-6666-4666-8666-666666666666',
    assignedToUserId: null,
    assignedToUserName: null,
    closedByUserId: null,
    closedAt: null,
    createdAt: '2026-09-14T10:00:00.000Z',
    updatedAt: '2026-09-14T10:00:00.000Z',
  };

  it('calcula o vencimento a partir da prioridade', () => {
    const sla = calculateTicketSla(ticket);

    expect(sla.dueAt).toBe(
      '2026-09-15T10:00:00.000Z',
    );
  });

  it('considera cumprido quando encerrado no prazo', () => {
    expect(
      wasTicketClosedWithinSla({
        ...ticket,
        status: 'closed',
        closedAt: '2026-09-15T09:59:59.000Z',
      }),
    ).toBe(true);
  });

  it('considera cumprido quando encerrado exatamente no vencimento', () => {
    expect(
      wasTicketClosedWithinSla({
        ...ticket,
        status: 'closed',
        closedAt: '2026-09-15T10:00:00.000Z',
      }),
    ).toBe(true);
  });

  it('considera violado quando encerrado depois do vencimento', () => {
    expect(
      wasTicketClosedWithinSla({
        ...ticket,
        status: 'closed',
        closedAt: '2026-09-15T10:00:01.000Z',
      }),
    ).toBe(false);
  });

  it('não considera cumprido um chamado sem data de encerramento', () => {
    expect(
      wasTicketClosedWithinSla(ticket),
    ).toBe(false);
  });

});