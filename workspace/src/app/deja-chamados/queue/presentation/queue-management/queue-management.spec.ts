import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  Ticket,
  TicketService,
} from '../../../tickets';

import {
  QueueManagementComponent,
} from './queue-management';

function createTicket(
  overrides: Partial<Ticket> = {},
): Ticket {
  return {
    id: 'ticket-1',
    organizationId: 'organization-1',
    tenantId: 'tenant-1',
    environmentId: 'environment-1',
    clientId: 'client-1',
    title: 'Chamado de teste',
    description: 'Descrição de teste',
    status: 'open',
    priority: 'high',
    openedByUserId: 'user-1',
    assignedToUserId: null,
    assignedToUserName: null,
    closedByUserId: null,
    closedAt: null,
    createdAt: '2026-09-01T10:00:00.000Z',
    updatedAt: '2026-09-01T10:00:00.000Z',
    ...overrides,
  };
}

describe('QueueManagementComponent', () => {

  let fixture: ComponentFixture<QueueManagementComponent>;
  let component: QueueManagementComponent;

  let listMock: ReturnType<typeof vi.fn>;
  let updateStatusMock: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    listMock = vi.fn();
    updateStatusMock = vi.fn();

    const service = {
      list: listMock,
      updateStatus: updateStatusMock,
    } as unknown as TicketService;

    await TestBed.configureTestingModule({
      imports: [
        QueueManagementComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      QueueManagementComponent,
    );

    component = fixture.componentInstance;

    fixture.componentRef.setInput(
      'service',
      service,
    );
  });

  it('não movimenta chamado sem permissão', async () => {
    const ticket = createTicket();

    component.tickets.set([ticket]);

    fixture.componentRef.setInput(
      'canManage',
      false,
    );

    await component.onTicketMoved({
      ticket,
      status: 'in_progress',
    });

    expect(updateStatusMock).not.toHaveBeenCalled();

    expect(
      component.tickets()[0].status,
    ).toBe('open');
  });

  it('persiste a mudança de status quando permitida', async () => {
    const ticket = createTicket();

    const updatedTicket = createTicket({
      status: 'in_progress',
      updatedAt: '2026-09-07T10:00:00.000Z',
    });

    component.tickets.set([ticket]);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateStatusMock.mockResolvedValue(
      updatedTicket,
    );

    await component.onTicketMoved({
      ticket,
      status: 'in_progress',
    });

    expect(updateStatusMock).toHaveBeenCalledWith(
      ticket.id,
      {
        status: 'in_progress',
      },
    );

    expect(
      component.tickets()[0],
    ).toEqual(updatedTicket);

    expect(
      component.operationMessage(),
    ).toBe('Status atualizado com sucesso.');
  });

  it('restaura o estado anterior quando a atualização falha', async () => {
    const ticket = createTicket();

    component.tickets.set([ticket]);

    fixture.componentRef.setInput(
      'canManage',
      true,
    );

    updateStatusMock.mockRejectedValue(
      new Error('Falha simulada'),
    );

    await component.onTicketMoved({
      ticket,
      status: 'pending',
    });

    expect(
      component.tickets()[0].status,
    ).toBe('open');

    expect(
      component.operationError(),
    ).toBe('Falha simulada');

    expect(
      component.updatingTicketId(),
    ).toBeNull();
  });

});
